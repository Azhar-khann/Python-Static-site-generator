class HTMLNODE:
    def __init__(self, tag = None, value = None, children = None, props = None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError("to_html method must be implemented by subclasses")
    
    def props_to_html(self):
        if self.props is None or len(self.props) == 0:
            return ""
        formatted_string =""
        for key, value in self.props.items():
            formatted_string += f' {key}="{value}"'
        return formatted_string
    
    def __repr__(self):
        return f"HTMLNODE(tag={self.tag}, value={self.value}, children={self.children}, props={self.props})"
    


class LeafNode(HTMLNODE):
    def __init__(self, tag, value , props = None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if self.value is None:
            raise ValueError("Leaf nodes must have a value")
        if self.tag is None:
            return f"{self.value}"
        
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
    
    def __repr__(self):
        return f"LeafNode(tag={self.tag}, value={self.value}, props={self.props})"
    


class ParentNode(HTMLNODE):
    def __init__(self, tag, children, props = None):
        super().__init__(tag, None, children, props)
    
    # purely done by me 
    def to_html(self):
        if self.tag is None:
            raise ValueError("Parent nodes must have a tag")
        if self.children is None or len(self.children) == 0:
            raise ValueError("Parent nodes must have children")
        
        childrens = ''
        for child in self.children:
            childrens += child.to_html()
        
        if self.tag == "img":
            return f"<{self.tag}{self.props_to_html()}{childrens}>"
        else:
            return f"<{self.tag}{self.props_to_html()}>{childrens}</{self.tag}>"

    
    def __repr__(self):
        return f"ParentNode(tag={self.tag}, children={self.children}, props={self.props})"