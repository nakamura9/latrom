import React, { Component } from 'react';
import $ from 'jquery';
import axios from 'axios';

//proptypes

class MultipleSelectWidget extends Component{ 
    
    state ={
        sourceList: [],
        selectedList: []
    }

    sourceClickHandler = (index) =>{
        let updatedList = [...this.state.sourceList];
        updatedList[index].clicked = !updatedList[index].clicked;
        this.setState({sourceList: updatedList});
    }
    
    selectedClickHandler = (index) =>{
        let updatedList = [...this.state.selectedList];
        updatedList[index].clicked = !updatedList[index].clicked;
        this.setState({selectedList: updatedList});
        
    }

    componentDidMount = () => {
        $('<input>').attr({
            name: this.props.inputField,
            type: 'hidden',
            value: encodeURIComponent(JSON.stringify([])),
            id: 'id_' + this.props.inputField
        }).appendTo('form')

        //first prepopulate the data 
        if(this.props.populatedURL){
            axios({
                url: this.props.populatedURL,
                method: 'GET'
            }).then((res) =>{
                const dataList = this.props.resProcessor(res);
                this.setState({selectedList: dataList}, () =>{
                    this.removeDuplicates();
                    this.updateForm();
                })
            })
        }
        //then make sure that no duplicates are found in the source list
        axios({
            url: this.props.dataURL,
            method: "GET"
        }).then(res => {
            const dataList =  res.data.map((item) => (
                {
                    value: item.id + '-' + item.name,
                    clicked: false
                }
            ))
            this.setState({sourceList: dataList}, this.removeDuplicates)
        });
    }

    removeDuplicates = () =>{
        const selectedListStrings = this.state.selectedList.map(e =>(e.value));
        const newSource = this.state.sourceList.filter((e) =>{
            return (!selectedListStrings.includes(e.value))
        });
        this.setState({sourceList: newSource});
    }

    updateForm =() =>{
        $('#id_'+ this.props.inputField).val(
            encodeURIComponent(
                JSON.stringify(this.state.selectedList)
            )
        );
    }
    selectHandler = () =>{
        let currentlySelected = this.state.sourceList.filter((element, i) =>{
            return (element.clicked);
        });
        let newSelected = this.state.selectedList.concat(currentlySelected);
        let newSource = this.state.sourceList.filter((element, i) =>{
            return (!element.clicked);
        })
        this.setState({
            selectedList: newSelected,
            sourceList: newSource
    }, this.updateForm);
    }

    removeHandler = () =>{
        let currentlySelected = this.state.selectedList.filter((element, i) =>{
            return (element.clicked);
        });
        let newSource = this.state.sourceList.concat(currentlySelected);
        let newSelected = this.state.selectedList.filter((element, i) =>{
            return (!element.clicked);
        })
        this.setState({
            selectedList: newSelected,
            sourceList: newSource
    }, this.updateForm);
    }

    render(){
        const optionContainer = {
            width: '150px',
            height: '200px',
            border: '1px solid grey',
            overflowY: 'scroll',
            float: 'left',
            display: 'inline',
            
        }
        return(
            <div>                    
                <h5>{this.props.title}</h5>
                <div style={{
                    display: "block",
                    clear: 'both',
                }}>
                    <div style={optionContainer}>
                        {this.state.sourceList.map((element, i) =>{
                            return(<ListItem 
                                key={i}
                                index={i}
                                data={element}
                                clickHandler={this.sourceClickHandler}/>)
                        })}
                    </div>
                    <div style={{float: 'left', width: '50px'}}>
                        <div style={{margin: "50px 5px"}}>
                            <button 
                                type="button"
                                style={{width: '100%'}}
                                onClick={this.selectHandler}>
                                <i className="fas fa-angle-right"></i>
                            </button>
                            <button 
                                type="button"
                                style={{width: '100%', marginTop: "10px"}}
                                onClick={this.removeHandler}>
                                <i className="fas fa-angle-left"></i>
                            </button>
                        </div>              
                    </div>
                    <div style={optionContainer}>
                        {this.state.selectedList.map((element, i) =>{
                            return(<ListItem 
                                key={i}
                                index={i}
                                data={element}
                                clickHandler={this.selectedClickHandler}/>);
                        })}
                    </div>
                </div>
            </div>
        )
    }
}

const ListItem = (props) =>{
    let commonStyle = {
        width: '100%',
        height: '30px',

    }
    let selectedStyle = {
        ...commonStyle,
        color: 'white',
        backgroundColor: '#07f'
    };
    let unselectedStyle = {...commonStyle};
    return(
        <div 
            style={props.data.clicked ? selectedStyle: unselectedStyle}
            onClick={() => props.clickHandler(props.index)}>
            {props.data.value}
        </div>
    )
}

export default MultipleSelectWidget;