import React, { Component } from "react";
import { Editor, EditorState, RichUtils, convertFromHTML, ContentState } from "draft-js";
import "draft-js/dist/Draft.css";
import styles from './richEditor.css';
import axios from 'axios';
import BlockStyleToolbar, {getBlockStyle} from '../components/block_style_toolbar';
//import ErrorBoundary from '../../src/components/error_boundary';

class EmailEditor extends Component {
  constructor(props) {
    super(props);
    this.state = {
      editorState: EditorState.createEmpty()
    };
  }

  componentDidMount(){
      if(this.props.prePopulatedURL){
          axios.get(this.props.prePopulatedURL).then(
              res =>{
                const blocksFromHTML = convertFromHTML(res.data.body)
                const state = ContentState.createFromBlockArray(
                    blocksFromHTML.contentBlocks,
                    blocksFromHTML.entityMap
                );
                this.setState(
                    {editorState: EditorState.createWithContent(state)},    
                        this.props.textHandler(this.state))
              }
          )
      }
  }

  

  onChange = (editorState) => {
     
     this.setState({ editorState }, this.props.textHandler(this.state));
    
    }

  handleKeyCommand = command => {
    const newState = RichUtils.handleKeyCommand(
      this.state.editorState,
      command
    );
    if (newState) {
      this.onChange(newState);
      return "handled";
    }

    return "not-handled";
  };

  toggleBlockType = (blockType) =>{
    this.onChange(RichUtils.toggleBlockType(this.state.editorState, blockType))
  }

  onItalicClick = () => {
    this.onChange(
      RichUtils.toggleInlineStyle(this.state.editorState, "ITALIC")
    );
  };

  onBoldClick = () => {
    this.onChange(
      RichUtils.toggleInlineStyle(this.state.editorState, "BOLD")
    );
  };

  onUnderlineClick = () => {
    this.onChange(
      RichUtils.toggleInlineStyle(this.state.editorState, "UNDERLINE")
    );
  };

  render() {
    return (
        <div id="editor-container" className={styles.editorContainer}>
        <BlockStyleToolbar
        editorState={this.state.editorState}
        onToggle={this.toggleBlockType} />
        
            <div id="editor-options" className="btn-group" style={{display: "inline-block"}}>
                <button 
                    type="button" 
                    className="btn" 
                    onClick={this.onItalicClick}><em>I</em></button>
                <button 
                    type="button" 
                    className="btn" 
                    onClick={this.onBoldClick}><b>B</b></button>
                <button 
                    type="button" 
                    className="btn" 
                    onClick={this.onUnderlineClick}>U</button>
            </div>
            <div id="editor-block" className={styles.editorBlock}>
                <Editor
                    blockStyleFn={getBlockStyle}
                    editorState={this.state.editorState}
                    onChange={this.onChange}
                    handleKeyCommand={this.handleKeyCommand}
                />
            </div>
        </div> 
    );
  }
}

export default EmailEditor;
