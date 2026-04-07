import asyncio
import json
import traceback
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
from src.config import Config

SERVER_URL = "http://localhost:2222/mcp"

async def safe_call_tool(session, tool_name, arguments):
    print(f"\n--- Testing {tool_name} ({arguments}) ---")
    try:
        result = await session.call_tool(tool_name, arguments=arguments)
        raw_text = result.content[0].text
        print(f"Raw response (first 200 chars): {raw_text[:200]}...")
        
        if raw_text.strip().startswith("Error"):
            print(f"Tool returned error: {raw_text}")
            return None
            
        try:
            data = json.loads(raw_text)
            print("Response is valid JSON.")
            return data
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Full Raw Response: {raw_text}")
            return None
    except Exception as e:
        print(f"Tool call failed: {e}")
        return None

async def main():
    token = Config.MCP_SERVER_TOKEN
    print(f"Connecting to {SERVER_URL} with token={token[:5]}... (length {len(token)})")
    try:
        async with sse_client(SERVER_URL, headers={"Authorization": f"Bearer {token}"}) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                print("Initializing session...")
                await session.initialize()
                
                print("\n--- Listing Tools ---")
                tools_result = await session.list_tools()
                tools = tools_result.tools
                print(f"Found {len(tools)} tools")
                
                # 1. List Courses
                courses_data = await safe_call_tool(session, "list_courses", {"per_page": 5})
                if not courses_data:
                    return

                print(f"Courses found: {len(courses_data)}")
                course = courses_data[0]
                course_id = str(course['id'])
                
                # 2. Get Course
                await safe_call_tool(session, "get_course", {"course_id": course_id})

                # 3. List Assignments
                assign_data = await safe_call_tool(session, "list_assignments", {"course_id": course_id, "per_page": 5})
                
                if assign_data:
                    print(f"Assignments found: {len(assign_data)}")
                    assign_id = str(assign_data[0]['id'])
                    # 4. Get Assignment
                    await safe_call_tool(session, "get_assignment", {"course_id": course_id, "assignment_id": assign_id})

                # 5. List Files
                files_data = await safe_call_tool(session, "list_files", {"course_id": course_id, "per_page": 5})
                
                if files_data and isinstance(files_data, list):
                    print(f"Files found: {len(files_data)}")
                    file_id = str(files_data[0]['id'])
                    # 6. Get File
                    await safe_call_tool(session, "get_file", {"file_id": file_id})
                    
                    # Try read_pdf
                    pdf_file = next((f for f in files_data if f.get('output_content_type', '').endswith('pdf') or f.get('filename', '').endswith('.pdf')), None)
                    if pdf_file:
                         pdf_id = str(pdf_file['id'])
                         await safe_call_tool(session, "read_pdf", {"file_id": pdf_id, "max_chars": 100})

                # 7. List Modules
                modules_data = await safe_call_tool(session, "list_modules", {"course_id": course_id, "include": ["items"], "per_page": 2})
                
                # Try to find a file in the modules
                if modules_data:
                    for module in modules_data:
                        for item in module.get("items", []):
                            if item.get("type") == "File":
                                file_id = str(item.get("content_id")) # content_id is usually the file ID for type File
                                print(f"Found file in module: {item.get('title')} (ID: {file_id})")
                                await safe_call_tool(session, "get_file", {"file_id": file_id})
                                # Test reading PDF
                                await safe_call_tool(session, "read_pdf", {"file_id": file_id, "max_chars": 100})
                                # Break after trying one file
                                break
                        else:
                            continue
                        break

                # 8. List Pages
                pages_data = await safe_call_tool(session, "list_pages", {"course_id": course_id, "per_page": 2})
                if pages_data and isinstance(pages_data, list):
                    page_url = pages_data[0]['url']
                    await safe_call_tool(session, "get_page", {"course_id": course_id, "page_url": page_url})

                # 9. List Folders
                folders_data = await safe_call_tool(session, "list_folders", {"course_id": course_id, "per_page": 2})
                if folders_data:
                     folder_id = str(folders_data[0]['id'])
                     await safe_call_tool(session, "get_folder", {"folder_id": folder_id})

                # 10. List Quizzes
                quizzes_data = await safe_call_tool(session, "list_quizzes", {"course_id": course_id, "per_page": 2})
                if quizzes_data:
                    quiz_id = str(quizzes_data[0]['id'])
                    await safe_call_tool(session, "get_quiz", {"course_id": course_id, "quiz_id": quiz_id})
                
                # 11. Social
                await safe_call_tool(session, "list_discussion_topics", {"course_id": course_id, "per_page": 2})
                await safe_call_tool(session, "list_announcements", {"course_id": course_id, "per_page": 2})
                await safe_call_tool(session, "list_todo", {"per_page": 2})
                await safe_call_tool(session, "list_calendar_events", {"per_page": 2})

    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
