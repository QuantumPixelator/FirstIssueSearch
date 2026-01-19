"""
GitHub Beginner Issue Finder

Searches GitHub for beginner-friendly issues across multiple languages and tags.
Displays results in a paginated GUI with clickable links.

Usage: pythonw search.py (Windows) or python search.py
"""
import os
import threading
import time
import datetime
import webbrowser
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests

# Config
DEFAULT_DAYS = 90
ITEMS_PER_PAGE = 25
CONFIG_FILE = "label_config.json"
DEFAULT_TAGS = ["good first issue", "good-first-issue", "beginner"]

TOP_LANGUAGES = [
    "JavaScript", "Python", "Java", "TypeScript", "C#", "PHP", "C++", "Shell", "Go",
    "Ruby", "C", "Kotlin", "Rust", "Scala", "Swift", "Objective-C", "PowerShell", "Dart", "Lua"
]

def load_labels():
    """Load saved labels from config file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f).get('labels', DEFAULT_TAGS)
        except:
            return DEFAULT_TAGS.copy()
    return DEFAULT_TAGS.copy()

def save_labels(labels):
    """Save labels to config file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'labels': labels}, f, indent=2)
        return True
    except:
        return False

def build_label_query(labels):
    """Build GitHub search query for labels. Uses first label only due to API limitations."""
    if not labels:
        return 'label:"good first issue"'
    return f'label:"{labels[0]}"'

def iso_date_days_ago(days):
    """Return ISO date string for N days ago."""
    dt = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    return dt.date().isoformat()

def gh_headers(token):
    """Build GitHub API headers."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    return headers

def search_open_beginner_issues(languages, days, labels, custom_terms, token, max_pages=10):
    """Search GitHub for open issues matching criteria.
    
    Returns dict mapping repo name to issue data.
    """
    url = "https://api.github.com/search/issues"
    updated_since = iso_date_days_ago(days)
    
    label_query = build_label_query(labels)
    query_parts = [
        "is:issue",
        "is:open",
        label_query,
        f"updated:>{updated_since}"
    ]
    
    if custom_terms and custom_terms.strip():
        query_parts.append(custom_terms.strip())
    
    # Add language filters
    if languages:
        if len(languages) == 1:
            query_parts.append(f"language:{languages[0]}")
        else:
            lang_query = "(" + " OR ".join([f"language:{lang}" for lang in languages]) + ")"
            query_parts.append(lang_query)
    
    query = " ".join(query_parts)
    repos_dict = {}
    per_page = 100
    
    for page in range(1, max_pages + 1):
        params = {"q": query, "sort": "updated", "order": "desc", "per_page": per_page, "page": page}
        resp = requests.get(url, headers=gh_headers(token), params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        
        for issue in items:
            repo_url = issue.get("repository_url")
            if not repo_url:
                continue
            
            # Parse repo info from URL
            parts = repo_url.split("/")
            if len(parts) >= 2:
                owner = parts[-2]
                repo_name = parts[-1]
                full_name = f"{owner}/{repo_name}"
            else:
                continue
            
            repo_info = {
                "full_name": full_name,
                "html_url": f"https://github.com/{full_name}",
                "description": "",
                "pushed_at": issue.get("updated_at", ""),
                "fork": False
            }
            
            if full_name not in repos_dict:
                repos_dict[full_name] = {
                    "repo_info": repo_info,
                    "issues_count": 0,
                    "sample_issue": issue.get("html_url")
                }
            
            repos_dict[full_name]["issues_count"] += 1
        
        if len(items) < per_page:
            break
        
        time.sleep(0.2)
    
    return repos_dict

# -------------------------
# GUI Implementation
# -------------------------
class App:
    def __init__(self, root):
        self.root = root
        root.title("🚀 GitHub Beginner Issue Finder")
        root.geometry("800x600")
        root.configure(bg="#f5f5f5")
        
        self._setup_styles()
        
        self.all_results = []
        self.current_page = 0
        self._tag_to_url = {}
        self._lock = threading.Lock()
        
        self.custom_labels = load_labels()
        
        # Language selection vars
        self.lang_vars = {}
        for lang in TOP_LANGUAGES:
            self.lang_vars[lang] = tk.BooleanVar(value=False)
        
        # Tag selection vars
        self.tag_var = tk.StringVar(value=DEFAULT_TAGS[0])
        self.custom_tag_var = tk.StringVar(value="")
        
        main_container = tk.Frame(root, bg="#f5f5f5")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header = tk.Frame(main_container, bg="#34495e", relief=tk.FLAT, bd=0)
        header.pack(fill=tk.X, pady=(0, 15))
        
        header_label = tk.Label(
            header, 
            text="GitHub Beginner Issue Finder",
            font=("Segoe UI", 16, "bold"),
            bg="#34495e",
            fg="white",
            pady=12
        )
        header_label.pack()
        
        # Controls panel
        controls_frame = tk.Frame(main_container, bg="white", relief=tk.FLAT, bd=0)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        controls = tk.Frame(controls_frame, bg="white", padx=20, pady=15)
        controls.pack(fill=tk.X)
        
        # Language section
        row1 = tk.Frame(controls, bg="white")
        row1.pack(fill=tk.X, pady=(0, 12))
        
        lang_header = tk.Frame(row1, bg="white")
        lang_header.pack(fill=tk.X, pady=(0, 5))
        tk.Label(lang_header, text="🌐 Languages", font=("Segoe UI", 10, "bold"), bg="white", fg="#2c3e50").pack(side=tk.LEFT)
        tk.Label(lang_header, text="(leave unchecked for all)", font=("Segoe UI", 8), bg="white", fg="#7f8c8d").pack(side=tk.LEFT, padx=(8, 0))
        
        lang_grid = tk.Frame(row1, bg="white")
        lang_grid.pack(fill=tk.X, pady=(0, 5))
        
        cols = 10
        for idx, lang in enumerate(TOP_LANGUAGES):
            row = idx // cols
            col = idx % cols
            cb = tk.Checkbutton(lang_grid, text=lang, variable=self.lang_vars[lang], bg="white", font=("Segoe UI", 8), activebackground="white")
            cb.grid(row=row, column=col, sticky=tk.W, padx=3, pady=1)
        
        custom_lang_frame = tk.Frame(row1, bg="white")
        custom_lang_frame.pack(fill=tk.X)
        tk.Label(custom_lang_frame, text="Custom:", font=("Segoe UI", 9), bg="white", fg="#555").pack(side=tk.LEFT, padx=(0, 5))
        self.custom_lang_var = tk.StringVar(value="")
        self.custom_lang_entry = ttk.Entry(custom_lang_frame, textvariable=self.custom_lang_var, width=20, style="Custom.TEntry")
        self.custom_lang_entry.pack(side=tk.LEFT)
        
        # Tag selection
        row2 = tk.Frame(controls, bg="white")
        row2.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(row2, text="🏷️  Issue Tag", font=("Segoe UI", 10, "bold"), bg="white", fg="#2c3e50").pack(anchor=tk.W, pady=(0, 5))
        
        tag_frame = tk.Frame(row2, bg="white")
        tag_frame.pack(fill=tk.X, pady=(0, 5))
        
        for tag in DEFAULT_TAGS:
            rb = tk.Radiobutton(tag_frame, text=tag, variable=self.tag_var, value=tag, bg="white", font=("Segoe UI", 9), activebackground="white")
            rb.pack(side=tk.LEFT, padx=(0, 15))
        
        custom_tag_frame = tk.Frame(row2, bg="white")
        custom_tag_frame.pack(fill=tk.X)
        
        rb_custom = tk.Radiobutton(custom_tag_frame, text="Custom:", variable=self.tag_var, value="__CUSTOM__", bg="white", font=("Segoe UI", 9), activebackground="white")
        rb_custom.pack(side=tk.LEFT, padx=(0, 5))
        
        self.custom_tag_entry = ttk.Entry(custom_tag_frame, textvariable=self.custom_tag_var, width=25, style="Custom.TEntry")
        self.custom_tag_entry.pack(side=tk.LEFT)
        self.custom_tag_entry.bind("<FocusIn>", lambda e: self.tag_var.set("__CUSTOM__"))
        
        # Search options
        row3 = tk.Frame(controls, bg="white")
        row3.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(row3, text="🔍 Search Terms:", font=("Segoe UI", 9, "bold"), bg="white", fg="#2c3e50").pack(side=tk.LEFT, padx=(0, 5))
        self.custom_terms_var = tk.StringVar(value="")
        self.custom_terms_entry = ttk.Entry(row3, textvariable=self.custom_terms_var, width=30, style="Custom.TEntry")
        self.custom_terms_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(row3, text="📅 Days:", font=("Segoe UI", 9, "bold"), bg="white", fg="#2c3e50").pack(side=tk.LEFT, padx=(0, 5))
        self.days_var = tk.IntVar(value=DEFAULT_DAYS)
        self.days_entry = ttk.Entry(row3, textvariable=self.days_var, width=8, style="Custom.TEntry")
        self.days_entry.pack(side=tk.LEFT)
        
        # Token
        row4 = tk.Frame(controls, bg="white")
        row4.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(row4, text="🔑 GitHub Token:", font=("Segoe UI", 9, "bold"), bg="white", fg="#2c3e50").pack(side=tk.LEFT, padx=(0, 5))
        self.token_var = tk.StringVar(value=os.getenv("GITHUB_TOKEN", ""))
        self.token_entry = ttk.Entry(row4, textvariable=self.token_var, show="*", width=50, style="Custom.TEntry")
        self.token_entry.pack(side=tk.LEFT)
        tk.Label(row4, text="(optional)", font=("Segoe UI", 8), bg="white", fg="#999").pack(side=tk.LEFT, padx=(5, 0))
        
        # Search button
        btn_container = tk.Frame(controls, bg="white")
        btn_container.pack(pady=(5, 0))
        
        self.fetch_btn = tk.Button(
            btn_container,
            text="Search Issues",
            command=self.on_fetch,
            font=("Segoe UI", 11, "bold"),
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            bd=0,
            padx=40,
            pady=10,
            cursor="hand2",
            activebackground="#2980b9",
            activeforeground="white"
        )
        self.fetch_btn.pack()
        
        # Status bar
        status_frame = tk.Frame(main_container, bg="#ecf0f1", relief=tk.FLAT, bd=0)
        status_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.status_var = tk.StringVar(value="Ready to search")
        self.status_label = tk.Label(status_frame, textvariable=self.status_var, font=("Segoe UI", 9), 
                                      bg="#ecf0f1", fg="#555", anchor=tk.W, padx=15, pady=6)
        self.status_label.pack(fill=tk.X)
        
        # Results section
        results_container = tk.Frame(main_container, bg="white", relief=tk.FLAT, bd=1, 
                                      highlightbackground="#ddd", highlightthickness=1)
        results_container.pack(fill=tk.BOTH, expand=True)
        
        results_header = tk.Frame(results_container, bg="#f8f9fa")
        results_header.pack(fill=tk.X)
        
        self.results_title_var = tk.StringVar(value="Results")
        results_title = tk.Label(results_header, textvariable=self.results_title_var, font=("Segoe UI", 10, "bold"),
                                 bg="#f8f9fa", fg="#2c3e50", pady=8, padx=15, anchor=tk.W)
        results_title.pack(fill=tk.X)
        
        self.results = scrolledtext.ScrolledText(results_container, wrap=tk.WORD, font=("Consolas", 10),
                                                  bg="#fafafa", fg="#2c3e50", relief=tk.FLAT, padx=15, pady=15)
        self.results.pack(fill=tk.BOTH, expand=True)
        
        # Text styling
        self.results.tag_configure("title", foreground="#2980b9", font=("Segoe UI", 11, "bold"), underline=True)
        self.results.tag_configure("description", foreground="#555", font=("Segoe UI", 9))
        self.results.tag_configure("meta", foreground="#7f8c8d", font=("Segoe UI", 9))
        self.results.tag_configure("issue_link", foreground="#e67e22", font=("Segoe UI", 9), underline=True)
        self.results.tag_configure("separator", foreground="#bdc3c7")
        self.results.tag_bind("title", "<Button-1>", self._on_title_click)
        self.results.tag_bind("issue_link", "<Button-1>", self._on_issue_link_click)
        self.results.config(state=tk.DISABLED, cursor="arrow")
        
        # Pagination
        pagination_frame = tk.Frame(results_container, bg="#f8f9fa", relief=tk.FLAT)
        pagination_frame.pack(fill=tk.X, pady=8, padx=10)
        
        self.prev_btn = tk.Button(pagination_frame, text="◀ Previous", command=self.prev_page, font=("Segoe UI", 9),
                                   bg="#3498db", fg="white", relief=tk.FLAT, bd=0, padx=15, pady=6, cursor="hand2",
                                   state=tk.DISABLED, activebackground="#2980b9", activeforeground="white")
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.page_info_var = tk.StringVar(value="")
        self.page_info_label = tk.Label(pagination_frame, textvariable=self.page_info_var, font=("Segoe UI", 9),
                                         bg="#f8f9fa", fg="#555")
        self.page_info_label.pack(side=tk.LEFT, expand=True)
        
        self.next_btn = tk.Button(pagination_frame, text="Next ▶", command=self.next_page, font=("Segoe UI", 9),
                                   bg="#3498db", fg="white", relief=tk.FLAT, bd=0, padx=15, pady=6, cursor="hand2",
                                   state=tk.DISABLED, activebackground="#2980b9", activeforeground="white")
        self.next_btn.pack(side=tk.RIGHT, padx=5)

    def _setup_styles(self):
        """Setup ttk widget styles."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.TLabel", font=("Segoe UI", 10, "bold"), background="white", foreground="#2c3e50")
        style.configure("Hint.TLabel", font=("Segoe UI", 8, "italic"), background="white", foreground="#7f8c8d")
        style.configure("Custom.TEntry", font=("Segoe UI", 10), fieldbackground="white", borderwidth=2)
        style.configure("Custom.TCombobox", font=("Segoe UI", 10), fieldbackground="white", borderwidth=2)
    
    def on_fetch(self):
        # Get selected languages
        selected_langs = [lang for lang, var in self.lang_vars.items() if var.get()]
        
        # Add custom language if provided
        custom_lang = self.custom_lang_var.get().strip()
        if custom_lang and custom_lang not in selected_langs:
            selected_langs.append(custom_lang)
        
        # Get selected tag (single selection)
        selected_tag = self.tag_var.get()
        if selected_tag == "__CUSTOM__":
            selected_tag = self.custom_tag_var.get().strip()
            if not selected_tag:
                messagebox.showwarning("No Tag", "Please enter a custom tag or select a pre-made tag!")
                return
        
        # Disable UI
        self.fetch_btn.config(state=tk.DISABLED)
        self.prev_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.DISABLED)
        self.results.config(state=tk.NORMAL)
        self.results.delete("1.0", tk.END)
        self.results.insert(tk.END, "🔄 Starting search...\n\nFetching repositories and checking for open beginner issues...\n")
        self.results.config(state=tk.DISABLED)
        self.status_var.set("Searching GitHub...")
        self.all_results = []
        self.current_page = 0
        # Start background thread
        t = threading.Thread(target=self._fetch_thread, daemon=True)
        t.start()

    def _fetch_thread(self):
        try:
            days = int(self.days_var.get())
            token = self.token_var.get().strip() or os.getenv("GITHUB_TOKEN")
            
            # Get selected languages
            selected_langs = [lang for lang, var in self.lang_vars.items() if var.get()]
            custom_lang = self.custom_lang_var.get().strip()
            if custom_lang and custom_lang not in selected_langs:
                selected_langs.append(custom_lang)
            
            # Get selected tag
            selected_tag = self.tag_var.get()
            if selected_tag == "__CUSTOM__":
                selected_tag = self.custom_tag_var.get().strip()
            
            custom_terms = self.custom_terms_var.get().strip()
            
            lang_desc = "all languages" if not selected_langs else ", ".join(selected_langs)
            
            self._append_status(f"Searching for OPEN issues with tag: {selected_tag}")
            self._append_result(f"🔍 Languages: {lang_desc}\n")
            self._append_result(f"🏷️  Tag: \"{selected_tag}\"\n")
            if custom_terms:
                self._append_result(f"🔎 Custom terms: {custom_terms}\n")
            self._append_result("\n")
            
            repos_dict = search_open_beginner_issues(selected_langs, days, [selected_tag], custom_terms, token, max_pages=10)
            
            if not repos_dict:
                self._append_result("No repositories found with OPEN issues matching your criteria.\n")
                self._done("No results found")
                return
            
            self._append_result(f"✓ Found {len(repos_dict)} repositories with matching open issues!\n\n")
            self._append_status("Processing results...")
            
            filtered_results = []
            for full_name, data in repos_dict.items():
                repo_info = data["repo_info"]
                filtered_results.append({
                    "full_name": repo_info["full_name"],
                    "html_url": repo_info["html_url"],
                    "description": repo_info["description"],
                    "pushed_at": repo_info["pushed_at"],
                    "fork": repo_info["fork"],
                    "beginner_issues_count": data["issues_count"],
                    "sample_issue": data["sample_issue"]
                })
            
            filtered_results.sort(key=lambda x: x["beginner_issues_count"], reverse=True)
            
            self.all_results = filtered_results
            self.current_page = 0
            self._display_current_page()
            self._done(f"Found {len(self.all_results)} repos with open issues")
            
        except Exception as e:
            self._append_result(f"\n❌ Error: {e}\n")
            self._done("Error occurred")
        finally:
            self.root.after(0, lambda: self.fetch_btn.config(state=tk.NORMAL))

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._display_current_page()
    
    def next_page(self):
        total_pages = (len(self.all_results) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self._display_current_page()
    
    def _display_current_page(self):
        if not self.all_results:
            return
        
        start_idx = self.current_page * ITEMS_PER_PAGE
        end_idx = min(start_idx + ITEMS_PER_PAGE, len(self.all_results))
        page_results = self.all_results[start_idx:end_idx]
        
        total_pages = (len(self.all_results) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        
        # Get selected tag for display
        selected_tag = self.tag_var.get()
        if selected_tag == "__CUSTOM__":
            selected_tag = self.custom_tag_var.get().strip() or "N/A"
        tags_display = selected_tag
        
        def _render():
            self.results.config(state=tk.NORMAL)
            self.results.delete("1.0", tk.END)
            self._tag_to_url.clear()
            
            # Page header
            page_header = f"✓ Showing {start_idx + 1}-{end_idx} of {len(self.all_results)} repositories with open issues\n"
            page_header += f"📋 Searched tags: {tags_display}\n"
            page_header += "─" * 100 + "\n\n"
            self.results.insert(tk.END, page_header, ("meta",))
            
            for i, r in enumerate(page_results, start=start_idx + 1):
                # Repository title (clickable)
                title = f"#{i}  {r['full_name']}"
                tag = f"title_{i}"
                self.results.insert(tk.END, title + "\n", ("title", tag))
                self._tag_to_url[tag] = r["html_url"]
                self.results.tag_bind(tag, "<Button-1>", self._on_title_click)
                self.results.tag_bind(tag, "<Enter>", lambda e: self.results.config(cursor="hand2"))
                self.results.tag_bind(tag, "<Leave>", lambda e: self.results.config(cursor="arrow"))
                
                desc = r["description"] or "No description available"
                if len(desc) > 120:
                    desc = desc[:120] + "..."
                self.results.insert(tk.END, f"    📝 {desc}\n", ("description",))
                
                pushed_date = r['pushed_at'].split('T')[0] if 'T' in r['pushed_at'] else r['pushed_at']
                meta_line = f"    📅 Last Update: {pushed_date}  |  🎯 Open Issues: {r['beginner_issues_count']}\n"
                self.results.insert(tk.END, meta_line, ("meta",))
                
                if r.get("sample_issue"):
                    issue_tag = f"issue_{i}"
                    self.results.insert(tk.END, f"    🔗 ", ("meta",))
                    self.results.insert(tk.END, "View an issue →", ("issue_link", issue_tag))
                    self.results.insert(tk.END, "\n", ("meta",))
                    self._tag_to_url[issue_tag] = r["sample_issue"]
                    self.results.tag_bind(issue_tag, "<Button-1>", self._on_issue_link_click)
                    self.results.tag_bind(issue_tag, "<Enter>", lambda e: self.results.config(cursor="hand2"))
                    self.results.tag_bind(issue_tag, "<Leave>", lambda e: self.results.config(cursor="arrow"))
                
                self.results.insert(tk.END, "\n" + "─" * 100 + "\n\n", ("separator",))
            
            self.results.config(state=tk.DISABLED)
            
            self.page_info_var.set(f"Page {self.current_page + 1} of {total_pages}")
            self.results_title_var.set(f"{len(self.all_results)} Repositories Found")
            
            self.prev_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
            self.next_btn.config(state=tk.NORMAL if self.current_page < total_pages - 1 else tk.DISABLED)
        
        self.root.after(0, _render)

    def _append_status(self, text):
        self.root.after(0, lambda: self.status_var.set(text))

    def _append_result(self, text):
        def _append():
            self.results.config(state=tk.NORMAL)
            self.results.insert(tk.END, text)
            self.results.see(tk.END)
            self.results.config(state=tk.DISABLED)
        self.root.after(0, _append)

    def _on_title_click(self, event):
        index = self.results.index(f"@{event.x},{event.y}")
        tags = self.results.tag_names(index)
        for t in tags:
            if t.startswith("title_"):
                url = self._tag_to_url.get(t)
                if url:
                    webbrowser.open(url)
                return
    
    def _on_issue_link_click(self, event):
        index = self.results.index(f"@{event.x},{event.y}")
        tags = self.results.tag_names(index)
        for t in tags:
            if t.startswith("issue_"):
                url = self._tag_to_url.get(t)
                if url:
                    webbrowser.open(url)
                return

    def _done(self, msg):
        self._append_status(msg)

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()