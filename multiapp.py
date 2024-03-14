"""Frameworks for running multiple Streamlit applications as a single app.
"""

class MultiApp:
    def __init__(self):
        self.apps = dict()

    def add_app(self, title, func):
        """Adds a new application.
        Parameters
        ----------
        func:
            the python function to render this app.
        title:
            title of the app. Appears in the dropdown in the sidebar.
        """
        self.apps[title] = {
            "title": title,
            "function": func
        }

    def run(self, title):
        args, kwargs = self.get_args(title)
        # print("PRINTING", title, args)
        self.apps[title]['function'](*args, **kwargs)
    
    def set_args(self, title, *args, **kwargs):
        self.apps[title]['args'] = args
        self.apps[title]['kwargs'] = kwargs
    
    def get_args(self, title):
        return self.apps[title]['args'], self.apps[title]['kwargs']
    
    def __str__(self) -> str:
        return f"MultiApp({', '.join(self.apps.keys())})"