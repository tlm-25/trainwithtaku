


from jinja2 import Environment, FileSystemLoader, Template
from email.mime.text import MIMEText
import os

HTML_TEMPLATE_FOLDER_PATH = "src/email_utils/templates"



def render_html_template(html_file_name:str,context:dict=None,template_folder_path:str=HTML_TEMPLATE_FOLDER_PATH)->Template:
    '''
    Read HTML file contents and render on web page. 

    :param html_file_name: name of the html file we want to read (assumes the file exists in template_folder_path)
    :param context: values to fill in template variables (e.g. {"name": "Alice"} replaces {{ name }} in the HTML)
    :param template_folder_path: Path to folder containing the template html files
    :returns: rendered HTML string with all template variables filled in

    '''
    # Look in the templates folder
    _loader = Environment(loader=FileSystemLoader(template_folder_path))

    html_template_file_path = template_folder_path+"/"+html_file_name

    if not os.path.exists(html_template_file_path):
        raise FileNotFoundError(f"Could not find '{html_template_file_path}'")

    return _loader.get_template(html_file_name).render(**context or {})
