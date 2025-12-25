import os
import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits import create_sql_agent
import pandas as pd
from sqlalchemy import create_engine, inspect
from pathlib import Path
import time
import plotly.express as px
import plotly.graph_objects as go

# LangSmith monitoring
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
from langsmith import traceable

def auto_visualize(df, query):
    """Auto-generate appropriate chart based on data structure"""
    if df is None or df.empty or len(df) == 0:
        return None, None
    
    try:
        # Get numeric and categorical columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Too many rows? Sample it
        if len(df) > 100:
            df_plot = df.head(100)
        else:
            df_plot = df.copy()
        
        # Decision logic for chart type
        fig = None
        chart_type = None
        
        # Case 1: Single numeric column (histogram)
        if len(numeric_cols) == 1 and len(categorical_cols) == 0:
            fig = px.histogram(df_plot, x=numeric_cols[0], title=f"Distribution of {numeric_cols[0]}")
            chart_type = "histogram"
        
        # Case 2: One categorical + one numeric (bar chart)
        elif len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            # Limit categories to top 20 for readability
            if df_plot[categorical_cols[0]].nunique() > 20:
                top_categories = df_plot.groupby(categorical_cols[0])[numeric_cols[0]].sum().nlargest(20).index
                df_plot = df_plot[df_plot[categorical_cols[0]].isin(top_categories)]
            
            fig = px.bar(df_plot, x=categorical_cols[0], y=numeric_cols[0],
                        title=f"{numeric_cols[0]} by {categorical_cols[0]}")
            chart_type = "bar"
        
        # Case 3: Multiple numeric columns (line chart if looks like time series, else scatter)
        elif len(numeric_cols) >= 2:
            # Check if first column could be time/sequence
            if df_plot[df_plot.columns[0]].is_monotonic_increasing:
                fig = px.line(df_plot, x=df_plot.columns[0], y=numeric_cols[1:],
                            title=f"Trend Analysis")
                chart_type = "line"
            else:
                fig = px.scatter(df_plot, x=numeric_cols[0], y=numeric_cols[1],
                               title=f"{numeric_cols[1]} vs {numeric_cols[0]}")
                chart_type = "scatter"
        
        # Case 4: Count/aggregation query (pie chart for top items)
        elif len(df_plot) <= 10 and len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            fig = px.pie(df_plot, names=categorical_cols[0], values=numeric_cols[0],
                        title=f"Distribution of {numeric_cols[0]}")
            chart_type = "pie"
        
        if fig:
            fig.update_layout(height=400)
            return fig, chart_type
        
    except Exception as e:
        # If auto-viz fails, just skip it
        return None, None
    
    return None, None

def run_agent(agent, context):
    """LangSmith-traceable agent invocation"""
    return agent.invoke({"input": context})

def show():
    # Initialize session state for database connection
    if "db_connected" not in st.session_state:
        st.session_state.db_connected = False
    if "db_agent" not in st.session_state:
        st.session_state.db_agent = None
    if "db_engine" not in st.session_state:
        st.session_state.db_engine = None
    if "db_url" not in st.session_state:
        st.session_state.db_url = ""
    if "db_tables" not in st.session_state:
        st.session_state.db_tables = []
    
    # Header
    st.title("💾 Database Query")
    st.write("Connect and query databases with natural language")
    
    st.divider()
    
    # Database Connection Section
    st.subheader("🔌 Database Connection")
    
    # Connection mode selection
    conn_mode = st.radio(
        "Connection Mode",
        ["Use Existing Database", "Custom Database URL"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if conn_mode == "Use Existing Database":
            # List available database files
            db_folder = Path("database")
            if db_folder.exists():
                db_files = list(db_folder.glob("*.db")) + list(db_folder.glob("*.sqlite"))
                if db_files:
                    db_file_names = [f.name for f in db_files]
                    selected_db = st.selectbox(
                        "Select Database",
                        db_file_names,
                        help="Choose from available database files"
                    )
                    db_url = f"sqlite:///{db_folder}/{selected_db}"
                    st.caption(f"**Path:** `{db_url}`")
                else:
                    st.warning("No database files found in database/ folder")
                    db_url = ""
            else:
                st.warning("database/ folder not found")
                db_url = ""
        else:
            # Custom URL input
            db_url = st.text_input(
                "Database URL",
                placeholder="Enter your database connection URL",
                help="Enter the connection string for your database"
            )
            st.caption("**Example:** `sqlite:///mydatabase.db` or `postgresql://user:pass@localhost/dbname`")
    
    with col2:
        st.write("")
        st.write("")
        connect_button = st.button("🔗 Connect", use_container_width=True)
    
    if connect_button:
        if db_url:
            with st.spinner("Connecting to database..."):
                try:
                    # Validate SQLite file exists before connecting
                    if db_url.startswith("sqlite:///"):
                        # Extract file path from URL
                        db_path = db_url.replace("sqlite:///", "")
                        if not Path(db_path).exists():
                            st.toast(f"Database file not found: {db_path}", icon="❌")
                            return
                    
                    # Test connection
                    engine = create_engine(db_url)
                    inspector = inspect(engine)
                    tables = inspector.get_table_names()
                    
                    # Setup agent
                    db = SQLDatabase.from_uri(db_url)
                    llm = ChatGoogleGenerativeAI(
                        model="gemini-3-flash-preview",
                        # model="gemini-2.5-flash",
                        google_api_key=os.getenv("GOOGLE_API_KEY"),
                        temperature=0,
                        convert_system_message_to_human=True
                    )
                    
                    agent = create_sql_agent(
                        llm=llm,
                        db=db,
                        agent_type="zero-shot-react-description",
                        verbose=True,
                        handle_parsing_errors=True,
                        max_iterations=3,  # Limit iterations for safety
                        early_stopping_method="generate"  # Stop if stuck
                    )
                    
                    # Save to session state
                    st.session_state.db_connected = True
                    st.session_state.db_agent = agent
                    st.session_state.db_engine = engine
                    st.session_state.db_url = db_url
                    st.session_state.db_tables = tables
                    
                    st.toast("Connected successfully!", icon="✅")
                    
                except Exception as e:
                    st.toast(f"Connection failed: {str(e)}", icon="❌")
        else:
            st.toast("Please enter a database URL", icon="⚠️")
    
    # Display database info and chat interface if connected
    if st.session_state.db_connected:
        # Get data from session state
        agent = st.session_state.db_agent
        engine = st.session_state.db_engine
        db_url = st.session_state.db_url
        tables = st.session_state.db_tables
        inspector = inspect(engine)
        
        # Display database info
        st.divider()
        st.subheader("📢 Database Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Database Type:** {db_url.split(':')[0].upper()}")
        
        with col2:
            st.info(f"**Total Tables:** {len(tables)}")
        
        # Tables list
        if tables:
            with st.expander("📋 Available Tables", expanded=False):
                # Collect table info
                table_data = []
                for idx, table in enumerate(tables, 1):
                    try:
                        # Get columns info
                        columns_info = inspector.get_columns(table)
                        col_count = len(columns_info)
                        col_names = ", ".join([col['name'] for col in columns_info])
                        # Get primary key
                        pk_constraint = inspector.get_pk_constraint(table)
                        pk = ", ".join(pk_constraint['constrained_columns']) if pk_constraint['constrained_columns'] else "-"
                        table_data.append({
                            "No": idx,
                            "Table": table,
                            "Columns": col_count,
                            "Primary Key": pk,
                            "Column Names": col_names
                        })
                    except Exception as e:
                        table_data.append({
                            "No": idx,
                            "Table": table,
                            "Columns": "N/A",
                            "Primary Key": "-",
                            "Column Names": "Error"
                        })
                # Display as dataframe
                df_tables = pd.DataFrame(table_data)
                st.dataframe(df_tables, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # Database Chat Section
        st.subheader("💬 Database Chat")
        
        # Query Examples
        with st.expander("💡 Example Questions", expanded=False):
            st.markdown("""
            Try asking questions like:
            - What are the top 3 most expensive products?
            - Show top 10 products by price.
            - Sales per month.
            """)
        
        st.divider()
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Display SQL query if available
                if message["role"] == "assistant" and "sql" in message:
                    with st.expander("View Generated SQL"):
                        st.code(message["sql"], language="sql")
                
                # Display chart if available
                if message["role"] == "assistant" and "chart" in message:
                    st.plotly_chart(message["chart"], use_container_width=True)
                    if "chart_type" in message:
                        st.caption(f"📊 Auto-generated {message['chart_type']} chart")
                
                # Display chart if available
                if message["role"] == "assistant" and "chart" in message:
                    st.plotly_chart(message["chart"], use_container_width=True)
                    if "chart_type" in message:
                        st.caption(f"📊 Auto-generated {message['chart_type']} chart")
        
        # Chat input
        query = st.chat_input("Ask a question about your database...", key="chat_input")
        
        if query:
            # Display user message
            with st.chat_message("user"):
                st.markdown(query)
            
            # Add to history
            st.session_state.messages.append({"role": "user", "content": query})
            
            # Get response with retry mechanism and validation
            with st.chat_message("assistant"):
                with st.spinner("🤔 Analyzing database..."):
                    max_retries = 2
                    retry_count = 0
                    success = False
                    
                    while retry_count <= max_retries and not success:
                        try:
                            # Add recent chat history to query context for follow-up questions
                            context = query
                            if len(st.session_state.messages) > 0:
                                # Get last 3 exchanges for context
                                recent_history = st.session_state.messages[-6:] if len(st.session_state.messages) >= 6 else st.session_state.messages
                                history_text = "\n".join([f"{msg['role']}: {msg['content'][:100]}" for msg in recent_history])
                                context = f"Previous conversation:\n{history_text}\n\nCurrent question: {query}"
                            
                            response = run_agent(agent, context)
                            answer = response["output"]
                            sql_query = None
                            
                            # Extract SQL query
                            if "intermediate_steps" in response:
                                for step in response["intermediate_steps"]:
                                    if len(step) >= 2:
                                        observation = step[1]
                                        if isinstance(observation, str):
                                            if "SELECT" in observation.upper() or "INSERT" in observation.upper():
                                                if sql_query is None:
                                                    sql_query = observation
                            
                            # Validation: Check if answer is valid
                            is_valid = True
                            validation_msg = ""
                            
                            if sql_query:
                                # Try to execute SQL and validate
                                try:
                                    result_df = pd.read_sql(sql_query, engine)
                                    
                                    # Validate: Check if result makes sense
                                    if result_df.empty and "count" not in query.lower() and "how many" not in query.lower():
                                        is_valid = False
                                        validation_msg = "Query returned no results. This might not be the correct answer."
                                except Exception as sql_error:
                                    is_valid = False
                                    validation_msg = f"SQL execution failed: {str(sql_error)}"
                            else:
                                # No SQL found - check if answer is meaningful
                                if len(answer.strip()) < 10 or "sorry" in answer.lower() or "cannot" in answer.lower():
                                    is_valid = False
                                    validation_msg = "Answer seems incomplete or unclear."
                            
                            # If validation fails and retries left, try again
                            if not is_valid and retry_count < max_retries:
                                retry_count += 1
                                st.warning(f"⚠️ {validation_msg} Retrying... (Attempt {retry_count + 1}/{max_retries + 1})")
                                time.sleep(1)
                                continue
                            
                            # Display answer
                            st.markdown(answer)
                            
                            # Display validation warning if last retry
                            if not is_valid and retry_count == max_retries:
                                st.warning(f"⚠️ Note: {validation_msg}")
                            
                            # Display results with auto-visualization
                            result_df = None
                            chart_fig = None
                            chart_type = None
                            
                            try:
                                if sql_query and "SELECT" in sql_query.upper():
                                    result_df = pd.read_sql(sql_query, engine)
                                    if not result_df.empty:
                                        st.dataframe(result_df, use_container_width=True)
                                        
                                        # Auto-generate chart
                                        chart_fig, chart_type = auto_visualize(result_df, query)
                                        if chart_fig:
                                            st.plotly_chart(chart_fig, use_container_width=True)
                                            st.caption(f"📊 Auto-generated {chart_type} chart")
                            except Exception as e:
                                pass
                            
                            # Save to message history
                            message_data = {"role": "assistant", "content": answer}
                            if sql_query:
                                message_data["sql"] = sql_query
                            if result_df is not None and not result_df.empty:
                                message_data["dataframe"] = result_df
                            if chart_fig:
                                message_data["chart"] = chart_fig
                                message_data["chart_type"] = chart_type
                            st.session_state.messages.append(message_data)
                            
                            success = True
                            
                        except Exception as e:
                            retry_count += 1
                            if retry_count <= max_retries:
                                st.warning(f"⚠️ Error occurred: {str(e)}. Retrying... (Attempt {retry_count + 1}/{max_retries + 1})")
                                time.sleep(1)
                            else:
                                error_msg = f"❌ Failed after {max_retries + 1} attempts: {str(e)}"
                                st.toast(f"Query failed: {str(e)}", icon="❌")
                                st.error(error_msg)
                                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                                success = True  # Exit loop

def run_agent(agent, context):
    """LangSmith-traceable agent invocation"""
    return agent.invoke({"input": context})
