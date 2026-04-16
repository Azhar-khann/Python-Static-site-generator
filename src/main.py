from split_blocks import markdown_to_blocks, markdown_to_html_node
from textnode import TextType, TextNode 
import shutil, os

# I Learned how to use f-strings in python so don't assume this must be implemented by AI

def main():
    dummy = TextNode("Hello World", TextType.TEXT)
    copy_static_to_public('static','public')
    generate_pages_recursive('content', 'template.html', 'public')
    #print(dummy.__repr__())



def copy_static_to_public(src,dest):
    
    if os.path.exists(dest):
        shutil.rmtree(dest)
        os.mkdir(dest)
    
    for something in os.listdir(src):
        if os.path.isfile(src + '/' + something):
            file = os.path.join(src, something)
            print('copying:', file , 'to', dest)
            shutil.copy(file, dest)
        else:
            new_destination = os.path.join(dest, something)
            new_source = os.path.join(src, something)
            os.mkdir(new_destination)
            copy_static_to_public(new_source, new_destination)


def extract_title(markdown):
    blocks = markdown_to_blocks(markdown)
    if blocks[0][0:2] != '# ':
        raise Exception("Markdown does not start with a title")
    title = blocks[0].removeprefix('# ').strip(' ')
    return title


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, "r") as f1, open(template_path, "r") as f2:
        markdown_content = f1.read()
        html_template = f2.read()

    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()

    title = extract_title(markdown_content)
    html_template = html_template.replace("{{ Title }}", title)\
    .replace("{{ Content }}", html_content)


    with open(dest_path, "w") as f:
        f.write(html_template)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    
    for something in os.listdir(dir_path_content):
        if os.path.isfile(dir_path_content + '/' + something):
            from_path = os.path.join(dir_path_content, something)
            dest_dir_path_filename = os.path.splitext(something)[0] + '.html'
            dest_path = os.path.join(dest_dir_path, dest_dir_path_filename)
            generate_page(from_path, template_path, dest_path)
        else:
            new_source = os.path.join(dir_path_content, something)
            new_destination = os.path.join(dest_dir_path, something)
            os.mkdir(new_destination)
            generate_pages_recursive(new_source, template_path, new_destination)


if __name__ == "__main__":
    main()