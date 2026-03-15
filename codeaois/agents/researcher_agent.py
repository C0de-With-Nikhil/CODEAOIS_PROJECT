import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
from codeaois.models.llm_interface import call_openrouter
from rich.console import Console

console = Console()

def search_and_scrape(query, num_results=2):
    """Searches the web and scrapes the text from the top results."""
    results_text = ""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))
            for res in results:
                url = res.get('href')
                title = res.get('title')
                results_text += f"\n--- Source: {title} ({url}) ---\n"
                
                try:
                    # Stealth headers to bypass basic bot-blockers
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                    page = requests.get(url, headers=headers, timeout=5)
                    soup = BeautifulSoup(page.content, 'html.parser')
                    
                    # Grab all the paragraph text
                    paragraphs = soup.find_all('p')
                    text = " ".join([p.get_text() for p in paragraphs])
                    
                    # Limit to 2500 characters per site to save your tokens
                    results_text += text[:2500] + "...\n"
                except Exception as e:
                    results_text += f"[Failed to scrape content from {url}]\n"
    except Exception as e:
        console.print(f"\n[bold red]✗ Search Engine Crash:[/bold red] {e}")
        return "WEB SEARCH FAILED. Tell the user you cannot search the internet due to an API error."
        
    return results_text

def generate_researcher_code(user_input, full_context=""):
    """Orchestrates the search, scrape, and synthesis process."""
    
    # 1. Ask the AI to figure out exactly what to search for
    query_prompt = f"Extract the core web search query from this prompt. Reply with ONLY the search string, no quotes.\nPrompt: {user_input}"
    search_query = call_openrouter("You are a search query extractor.", query_prompt, intent="chat", history=[])
    search_query = search_query.strip().strip('"').strip("'")
    
    console.print(f"[dim]🌐 Searching live web for: [bold white]{search_query}[/bold white][/dim]")
    
    # 2. Execute the live web search and scrape the pages
    web_context = search_and_scrape(search_query)
    
    # 3. Feed the live data back to the AI to answer the user
    console.print(f"[dim]📚 Reading scraped documentation...[/dim]")
    
    sys_prompt = "You are an expert AI Researcher with live internet access. Use the provided Web Research to answer the user accurately."
    final_prompt = f"LATEST WEB RESEARCH:\n{web_context}\n\nUSER REQUEST: {user_input}\nLOCAL CONTEXT:\n{full_context}"
    
    return call_openrouter(sys_prompt, final_prompt, intent="chat", history=[])