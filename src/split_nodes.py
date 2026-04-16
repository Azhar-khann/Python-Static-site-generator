from textnode import TextNode, TextType
import re

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    delimiter_text = []
    all_nodes = []
    opening = False
    text = ''
    delim_track = ''


    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            all_nodes.append(node)
            continue
        for char in node.text:
            if char == delimiter[0]:
                delim_track += char

            if delim_track == delimiter:
                opening = not opening
                delim_track = ''

            if opening == True and char != delimiter[0]:
                text += char
            
            if opening == False and len(text) >= 1:
                delimiter_text.append(text)
                text = ''
        
        if opening == True:
            raise Exception("Unmatched delimiter in text: ", node.text)
        
        all_text = node.text.split(delimiter)
        for text in all_text:
            if text in delimiter_text:
                all_nodes.append(TextNode(text, text_type))
            else:
                all_nodes.append(TextNode(text,TextType.TEXT))

    return all_nodes
    

def extract_markdown_images(text):
    return re.findall(r"\!\[(.*?)\]\((.*?)\)", text)


def extract_markdown_links(text):
    return re.findall(r"\[(.*?)\]\((.*?)\)", text)



def split_nodes_image(old_nodes):
    image_counter = 0
    all_nodes = []
    image_text = False
    text = ''


    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            all_nodes.append(node)
            continue
        links = extract_markdown_images(node.text)
        for i in range(len(node.text)):
            if node.text[i] == '!' and i < len(node.text) - 1 and node.text[i+1] == '[':
                image_text = True

            if image_text == False:
                text += node.text[i]

            if node.text[i] == ')' and image_text == True:
                image_text = False
                if len(text) >= 1:
                    all_nodes.append(TextNode(text,TextType.TEXT))
                all_nodes.append(TextNode(links[image_counter][0],TextType.IMAGE, links[image_counter][1]))
                text = ''
                image_counter += 1
        
        if len(text) >= 1:
            all_nodes.append(TextNode(text,TextType.TEXT))
        image_counter = 0
        text = ''
    return all_nodes
    

def split_nodes_link(old_nodes):
    link_counter = 0
    all_nodes = []
    link_text = False
    text = ''


    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            all_nodes.append(node)
            continue
        links = extract_markdown_links(node.text)
        for i in range(len(node.text)):
            if node.text[i] == '[' and node.text[i-1] != '!' :
                link_text = True

            if link_text == False:
                text += node.text[i]

            if node.text[i] == ')' and link_text == True:
                link_text = False
                if len(text) >= 1:
                    all_nodes.append(TextNode(text,TextType.TEXT))
                all_nodes.append(TextNode(links[link_counter][0],TextType.LINK, links[link_counter][1]))
                text = ''
                link_counter += 1
        
        if len(text) >= 1:
            all_nodes.append(TextNode(text,TextType.TEXT))
        link_counter = 0
        text = ''

    return all_nodes




def text_to_textnodes(text):
    node = [TextNode(text, TextType.TEXT)]

    nodes1 = split_nodes_image(node)
    nodes2 = split_nodes_link(nodes1)
  
    nodes3 = split_nodes_delimiter(nodes2, '**' ,TextType.BOLD)
    nodes4 = split_nodes_delimiter(nodes3, '_' ,TextType.ITALIC)
    nodes5 = split_nodes_delimiter(nodes4, '`' ,TextType.CODE)

    return nodes5


text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
result = text_to_textnodes(text)
#print(result)