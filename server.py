import os
from typing import Optional, Dict, Any, List
from mcp.server.fastmcp import FastMCP
from zfn_api import Client

# Initialize FastMCP server
mcp = FastMCP("Zhengfang System")

# Global client instance
_client: Optional[Client] = None

def get_client() -> Client:
    """
    Get or initialize the ZFN Client.
    Authentication is handled lazily using environment variables.
    """
    global _client
    
    # Return existing authenticated client if available
    if _client and _client.cookies:
        return _client

    # Initialize new client
    base_url = os.environ.get("ZFN_URL")
    if not base_url:
        raise ValueError("Environment variable ZFN_URL is not set.")
        
    client = Client(base_url=base_url)
    
    # Attempt login
    sid = os.environ.get("ZFN_SID")
    password = os.environ.get("ZFN_PASSWORD")
    
    if not sid or not password:
        raise ValueError("Environment variables ZFN_SID and ZFN_PASSWORD are required.")
    
    login_result = client.login(sid, password)
    
    if login_result.get("code") != 1000:
        # If login fails (e.g. wrong password or captcha needed which we can't handle yet easily)
        # Note: The original zfn_api might require captcha for some systems. 
        # For this implementation we assume standard login works or we fail.
        msg = login_result.get("msg", "Unknown error")
        raise RuntimeError(f"Login failed: {msg}")
        
    _client = client
    return _client

@mcp.tool()
def login_check() -> str:
    """
    Check if the current session is valid and login is successful.
    """
    try:
        client = get_client()
        # Verify by getting personal info, as it's a lightweight authenticated call
        result = client.get_info()
        if result.get("code") == 1000:
            return f"Login successful. User: {result['data'].get('name')} ({result['data'].get('sid')})"
        return f"Session check failed: {result.get('msg')}"
    except Exception as e:
        return f"Login check error: {str(e)}"

@mcp.tool()
def get_my_grades(year: int, term: int = 0) -> str:
    """
    Get grades for a specific year and term.
    
    Args:
        year: The academic year (e.g., 2023 for 2023-2024).
        term: The term number. 1 for first term, 2 for second term. 0 for the whole year.
    """
    try:
        client = get_client()
        # The zfn_api takes year and term. 
        # Note: The user prompt asked to handle logic where term=0 means whole year.
        # zfn_api.get_grade seems to handle term=0 internally (term=0 -> term="" -> whole year).
        # We pass it directly.
        
        result = client.get_grade(year, term)
        
        if result.get("code") == 1000:
            data = result["data"]
            courses = data.get("courses", [])
            if not courses:
                return f"No grades found for {year} term {term}."
                
            output = [f"Grades for {data['name']} ({year}-{term}):"]
            for c in courses:
                output.append(f"- {c['title']}: {c['grade']} (Credit: {c['credit']}, Point: {c['grade_point']})")
            return "\n".join(output)
        else:
            return f"Error getting grades: {result.get('msg')}"
            
    except Exception as e:
        return f"Error executing get_my_grades: {str(e)}"

@mcp.tool()
def get_my_schedule(year: int, term: int) -> str:
    """
    Get the class schedule for a specific year and term.
    
    Args:
        year: The academic year (e.g., 2023).
        term: The term number (1 or 2).
    """
    try:
        client = get_client()
        result = client.get_schedule(year, term)
        
        if result.get("code") == 1000:
            data = result["data"]
            courses = data.get("courses", [])
            output = [f"Schedule for {year} term {term}:"]
            for c in courses:
                output.append(f"- {c['title']} ({c['teacher']}): {c['weekday']} {c['time']} @ {c['place']}")
            return "\n".join(output)
        else:
            return f"Error getting schedule: {result.get('msg')}"
    except Exception as e:
        return f"Error executing get_my_schedule: {str(e)}"

@mcp.tool()
def get_student_info() -> str:
    """
    Get the student's personal information.
    """
    try:
        client = get_client()
        result = client.get_info()
        
        if result.get("code") == 1000:
            info = result["data"]
            return "\n".join([f"{k}: {v}" for k, v in info.items()])
        else:
            return f"Error getting student info: {result.get('msg')}"
    except Exception as e:
        return f"Error executing get_student_info: {str(e)}"

@mcp.tool()
def get_exam_schedule(year: int, term: int = 0) -> str:
    """
    Get the exam schedule for a specific year and term.
    
    Args:
        year: The academic year.
        term: The term number (1 or 2, 0 for whole year).
    """
    try:
        client = get_client()
        result = client.get_exam_schedule(year, term)
        
        if result.get("code") == 1000:
            data = result["data"]
            exams = data.get("courses", [])
            if not exams:
                return "No exams found."
                
            output = [f"Exam Schedule for {year} term {term}:"]
            for e in exams:
                output.append(
                    f"- {e['title']}: {e['time']} @ {e['location']} (Seat: {e.get('zwh', 'N/A')})"
                )
            return "\n".join(output)
        else:
            return f"Error getting exam schedule: {result.get('msg')}"
    except Exception as e:
        return f"Error executing get_exam_schedule: {str(e)}"

if __name__ == "__main__":
    mcp.run()
