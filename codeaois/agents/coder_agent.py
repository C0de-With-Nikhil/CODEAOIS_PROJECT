from codeaois.models.llm_interface import call_openrouter
from rich.console import Console
import time

console = Console()

def generate_code(user_input, full_context=""):
    """Multi-Agent Swarm that plans, writes, and reviews code."""
    
    # --- AGENT 1: THE ARCHITECT ---
    console.print(f"[dim]🧠 [Architect] Drafting system blueprint...[/dim]")
    architect_sys = "You are a Senior Software Architect. Break the user's request down into a strict, bulleted, step-by-step implementation plan. Identify the best programming language if not specified. Do NOT write code. Only write the logical plan."
    plan = call_openrouter(architect_sys, f"REQUEST: {user_input}\nCONTEXT: {full_context}", intent="chat", history=[])
    
    # Let the free API cool down!
    time.sleep(8) 
    
    # --- AGENT 2: THE DEVELOPER ---
    console.print(f"[dim]💻 [Developer] Writing code based on blueprint...[/dim]")
    dev_sys = "You are an Elite Polyglot Software Engineer. Write the complete, functional code based EXACTLY on the Architect's plan. Return ONLY the final code inside a markdown block. Do not add explanations."
    dev_prompt = f"ARCHITECT PLAN:\n{plan}\n\nWrite the code."
    raw_code = call_openrouter(dev_sys, dev_prompt, intent="code", history=[])
    
    # Let the free API cool down again!
    time.sleep(8) 
    
    # --- AGENT 3: THE QA TESTER ---
    console.print(f"[dim]🔎 [QA Tester] Auditing code for bugs and syntax errors...[/dim]")
    qa_sys = "You are a strict QA Code Reviewer. Review the provided code for logic errors, missing dependencies, or syntax issues. Fix any issues found. Return ONLY the final, perfect code inside a markdown block. No explanations."
    qa_prompt = f"ORIGINAL REQUEST: {user_input}\n\nDRAFT CODE:\n{raw_code}\n\nReview and return the final bulletproof code."
    final_code = call_openrouter(qa_sys, qa_prompt, intent="code", history=[])
    
    console.print("[bold green]✓ Swarm consensus reached![/bold green]")
    
    return final_code

def generate_lite_code(user_input, full_context=""):
    """Single-shot coder that bypasses the Swarm to prevent API rate limits."""
    console.print(f"[dim]⚡ [Fast Coder] Writing code in a single shot...[/dim]")
    
    dev_sys = """You are an Elite Software Engineer. Write the complete, functional code requested by the user. 
    You MUST output the target filename at the very top of your response (e.g., `### Filename: clock.html`).
    Then, provide ONLY the final code inside a markdown block. Do NOT add any conversational text or apologies."""
    
    # We use a single API call instead of 3, keeping you perfectly under the free rate limits!
    return call_openrouter(dev_sys, f"REQUEST: {user_input}\nCONTEXT: {full_context}", intent="code", history=[])