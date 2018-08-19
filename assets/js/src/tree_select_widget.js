import React, {Component} from 'react';
import axios from 'axios';
import $ from 'jquery';


const itemStyle = {
    width: "100%",
    padding: "3px",
    margin: "2px",
    backgroundColor: "#ddd",
    listStyleType: "none" 
}

export default class TreeSelectWidget extends Component{
    state = {
        selected: {
            label: "None",
            id: ""
        },
        data: []
    }

    componentDidMount(){
        axios({
            url: this.props.url,
            method: 'GET'
        }).then( res =>{
            let nodes = res.data.map(this.props.dataMapper);
            this.setState({data: nodes});
        });
        let field = document.getElementById('id_' + this.props.fieldName);
        if( field === null){
            $('<input>').attr({
                type: 'hidden',
                name: this.props.fieldName,
                id: 'id_' + this.props.fieldName,
                value: ''
            }).appendTo('form');
        }
    }

    selectHandler = (node) => {
        
        this.setState({selected: node}, () =>{
            this.updateForm();
            this.props.selectFunc(this.state.selected.id);
        });
    }

    updateForm = () =>{
        $('#id_' + this.props.fieldName).val(this.state.selected.id);
    }
    render(){
        return(
            <div>
                <ul style={{listStyleType: "none"}}>
                {this.state.data.map((element, i) => {
                    if(element.nodes.length === 0){
                        return <LeafNode 
                                    node={element} 
                                    key={i}
                                    selectHandler={this.selectHandler}/>
                    }else{
                        return <BranchNode 
                                    node={element} 
                                    key={i}
                                    mapper={this.props.dataMapper}
                                    selectHandler={this.selectHandler}/>
                    }
                })}
                </ul>
                <h5>Selected Node: {this.state.selected.label}</h5>
            </div>
        );
    }
}

class BranchNode  extends Component{
    state ={
        showChildren: false
    }
    clickHandler = () =>{
        this.setState({showChildren: !this.state.showChildren});
        this.props.selectHandler(this.props.node);
    }
    render(){
        let trasformedData = this.props.node.nodes.map(this.props.mapper);
        return(
            <li style={{listStyleType: "none"}}>
                <div 
                    style={itemStyle}
                    onClick={this.clickHandler}>{this.props.node.label}
                    <span style={{
                        float:'right',
                        margin: "3px"
                    }}>
                        <i className={this.state.showChildren
                            ? "fas fa-arrow-left"
                            : "fas fa-arrow-down"}></i>
                    </span>
                </div>
                <ul style={{
                    display: this.state.showChildren ? "block" : "none"
                }}>
                    {trasformedData.map((element, i) => {
                        if(element.nodes.length === 0){
                            return <LeafNode 
                                        node={element} 
                                        key={i}
                                        selectHandler={this.props.selectHandler}/>
                        }else{
                            return <BranchNode 
                                        node={element} 
                                        key={i}
                                        mapper={this.props.mapper}
                                        selectHandler={this.props.selectHandler}/>
                        }
                    })}
                </ul>
            </li>
        );
    }
}
    

const LeafNode = (props) =>{
    return(
        <li 
            style={itemStyle}
            onClick={() => props.selectHandler(props.node)}>
            {props.node.label}
        </li>
    );
}