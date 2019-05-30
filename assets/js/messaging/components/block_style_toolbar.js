import React from 'react';
import HeaderStyleDropdown from './header_style_dropdown';
import BlockStyleButton from './block_style_button';

export const BLOCK_TYPE_HEADINGS = [
    {label: 'H1', style:'header-one'},
    {label: 'H2', style:'header-two'},
    {label: 'H3', style:'header-three'},
    {label: 'H4', style:'header-four'},
    {label: 'H5', style:'header-five'},
    {label: 'H6', style:'header-six'}
]

export const BLOCK_TYPES = [
    {label: <i className="fas fa-list"></i>, style: "unordered-list-item"},
    {label: <i className="fas fa-list-ol"></i>, style: "ordered-list-item"},
]

export function getBlockStyle(block){
    switch(block.getType()){
        case 'block-quote':
            return "RichEditor-blockquote";
        default:
            return null;
    }
}

class BlockStyleToolbar extends React.Component{
    render(){
        const {editorState} = this.props;
        const selection = editorState.getSelection();
        const blockType = editorState.getCurrentContent()
            .getBlockForKey(selection.getStartKey())
            .getType();

        return (
            <div style={{display: 'inline-block', width: "50%"}}>
                <span className="RichEditor-controls">
                    <HeaderStyleDropdown 
                        headerOptions={BLOCK_TYPE_HEADINGS}
                        active={blockType}
                        onToggle={this.props.onToggle}
                        />
                    {BLOCK_TYPES.map(type =>{
                        return(
                            <BlockStyleButton 
                                active={type.style == blockType}
                                label={type.label}
                                onToggle={this.props.onToggle}
                                style={type.style}
                                key={type.style}
                                type={type}/>
                        )
                    })}
                    
                </span>
            </div>
        )
    }
}

export default BlockStyleToolbar;