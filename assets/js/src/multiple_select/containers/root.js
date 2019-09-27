import React, {Component} from "react";
import SelectedItemsListWidget from "../components/list_widget";
import SearchableTextInputWidget from "./text_input";
import axios from "axios";
import $ from "jquery";

/**
 * props
 *  input field -string naming the hidden input the widget adds to the form
 *  populatedURL - string
 *  resProcessor -function
 *  dataURL -string 
 *  nameField - string
 */

class MultipleSelectWidget extends Component{
    state = {
        selectedItems: [],
    }

    updateForm =() =>{
        if(this.props.selectHook){
         this.props.selectHook(this.state.selectedItems);
        }
        $('#id_'+ this.props.inputField).val(
            encodeURIComponent(
                JSON.stringify(this.state.selectedItems)
            )
        );
    }

    componentDidMount(){
        $('<input>').attr({
            name: this.props.inputField,
            type: 'hidden',
            value: encodeURIComponent(JSON.stringify([])),
            id: 'id_' + this.props.inputField
        }).appendTo('form');

        //first prepopulate the data 
        if(this.props.populatedURL){
            axios({
                url: this.props.populatedURL,
                method: 'GET'
            }).then((res) =>{
                const dataList = this.props.resProcessor(res);
                this.setState({selectedItems: dataList}, () =>{
                    //this.removeDuplicates();
                    this.updateForm();
                    
                })
            })
        }
    }

    addItem = (value) =>{
        let newItems = [...this.state.selectedItems];
        newItems.push(value);
        this.setState({selectedItems: newItems}, this.updateForm);
    }

    removeHandler = (index) =>{
        let newItems = [...this.state.selectedItems];
        newItems.splice(index, 1);
        this.setState({selectedItems: newItems});
    }
    
    render(){
        
        return(
            <div>
                <SearchableTextInputWidget
                    nameField={this.props.nameField}
                    idField={this.props.idField}
                    dataURL={this.props.dataURL} 
                    newLink={this.props.newLink}
                    addItem={this.addItem}/>
                <SelectedItemsListWidget 
                    removeHandler={this.removeHandler}
                    selectedItems={this.state.selectedItems}/>
            </div>
        )
    }
}

export default MultipleSelectWidget;