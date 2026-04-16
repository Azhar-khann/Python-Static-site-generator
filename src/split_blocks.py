from enum import Enum

from htmlnode import LeafNode, ParentNode
from split_nodes import text_to_textnodes
from textnode import text_node_to_html_node

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def markdown_to_blocks(markdown):
    blocks = markdown.split('\n\n')
    for i in range(len(blocks)):
        blocks[i] = blocks[i].strip()
    blocks = [block for block in blocks if block != '']
    return blocks

def block_to_block_type(block):

    if block[0:2] == '# ' or block[0:3] == '## ' or block[0:4] == '### ' or block[0:5] == '#### ' or block[0:6] == '##### ' or block[0:7] == '###### ':
        return BlockType.HEADING
    
    if block[0:4] == '```\n' and block[-4:] == '\n```':
        return BlockType.CODE
    
    if block[0] == '>':
        lines = block.split('\n')
        count = 0
        for line in lines:
            if line[0] == '>':
                count += 1
        if count == len(lines):
            return BlockType.QUOTE
    

    if block[0:2] == '- ':
        count = 0
        lines = block.split('\n')
        for line in lines:
            if line[0:2] == '- ':
                count += 1
        if count == len(lines):
            return BlockType.UNORDERED_LIST
    
    
    if block[0] == '1':
        count = 1
        lines = block.split('\n')
        for line in lines:
            if line[0:len(str(count))+2] == str(count) + '. ':
                count += 1
        if count - 1 == len(lines):
            return BlockType.ORDERED_LIST

    
    return BlockType.PARAGRAPH



def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    html_nodes = []
    block_html_nodes = []

    for block in blocks:

        if block_to_block_type(block) == BlockType.PARAGRAPH:
            text_nodes = text_to_textnodes(block)
            for text_node in text_nodes:
                html_node = text_node_to_html_node(text_node)
                if html_node.tag != "img":
                    html_node.value = html_node.value.replace('\n', ' ')
                    block_html_nodes.append(html_node)
                else:
                    node = LeafNode(None, f' src="{html_node.props["src"]}" alt="{html_node.props["alt"]}"')
                    block_html_nodes.append(ParentNode("img", [node]))
            block_parent_node = ParentNode("p", block_html_nodes)
            block_html_nodes = []
            html_nodes.append(block_parent_node)
        
        if block_to_block_type(block) == BlockType.HEADING:
            heading = 'h' + str(block[0:7].count('#'))
            text_nodes = text_to_textnodes(block)
            for text_node in text_nodes:
                html_node = text_node_to_html_node(text_node)
                block_html_nodes.append(html_node)
            block_html_nodes[0].value = block_html_nodes[0].value.lstrip('#').lstrip()

            block_parent_node = ParentNode(heading, block_html_nodes)
            block_html_nodes = []
            html_nodes.append(block_parent_node)

        if block_to_block_type(block) == BlockType.QUOTE:
            text_nodes = text_to_textnodes(block)
            for text_node in text_nodes:
                html_node = text_node_to_html_node(text_node)
                html_node.value = html_node.value.replace('> ', '')
                html_node.value = html_node.value.replace('>', '')
                block_html_nodes.append(html_node)
            block_parent_node = ParentNode("blockquote", block_html_nodes)
            block_html_nodes = []
            html_nodes.append(block_parent_node)

        if block_to_block_type(block) == BlockType.UNORDERED_LIST:
            # split by '\n-' to get each item - each item becomes as if it's a separate block and we can reuse the same code as before to convert each item into html nodes and then wrap all those nodes in a parent node with tag 'ul' and each item node wrapped in a parent node with tag 'li'
            item_blocks = block.split('\n')
            item_block_parent = []
            for item_block in item_blocks:
                text_nodes = text_to_textnodes(item_block)
                for text_node in text_nodes:
                    html_node = text_node_to_html_node(text_node)
                    if html_node.tag != "img":
                        html_node.value = html_node.value.removeprefix('- ')                 
                        block_html_nodes.append(html_node)      
                    else:
                        node = LeafNode(None, f' src="{html_node.props["src"]}" alt="{html_node.props["alt"]}"')
                        block_html_nodes.append(ParentNode("img", [node]))          
                item_block_parent.append(ParentNode("li" , block_html_nodes))
                block_html_nodes = []
            block_parent_node = ParentNode("ul", item_block_parent)
            html_nodes.append(block_parent_node)


        if block_to_block_type(block) == BlockType.ORDERED_LIST:
            # split by '\n-' to get each item - each item becomes as if it's a separate block and we can reuse the same code as before to convert each item into html nodes and then wrap all those nodes in a parent node with tag 'ul' and each item node wrapped in a parent node with tag 'li'
            item_blocks = block.split('\n')
            item_block_parent = []
            count = 1
            for item_block in item_blocks:
                text_nodes = text_to_textnodes(item_block)
                for text_node in text_nodes:
                    html_node = text_node_to_html_node(text_node)
                    html_node.value = html_node.value.removeprefix(str(count) + '. ')
                    block_html_nodes.append(html_node)  
                count += 1              
                item_block_parent.append(ParentNode("li" , block_html_nodes))
                block_html_nodes = []
            block_parent_node = ParentNode("ol", item_block_parent)
            html_nodes.append(block_parent_node)

        
        if block_to_block_type(block) == BlockType.CODE:
            code_text = block.replace('```','')
            code_text = code_text[1:]
            code_node = LeafNode('code', code_text)
            block_parent_node = ParentNode("pre", [code_node])
            html_nodes.append(block_parent_node)


    return ParentNode("div", html_nodes)

node = markdown_to_html_node(">no space quote")
html = node.to_html()
#print(html)

""" blocks = markdown_to_blocks(md)
print('type =',block_to_block_type(blocks[0]))
print(blocks[0].split('\n')) """
