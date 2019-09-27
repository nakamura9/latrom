import React, {Component} from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
/**
 * props 
 * dataURL - string with the data that populates the form
 * name - string that sets the name attribute in the select 
 * resProcessor - a function that takes the axios res and returns an array of 
 *                  value name objects
 * onPopulated - optional attr that provides an initial value of the form
 * handler - the function that is called when the select is changed.
 */


class AsyncSelect extends Component{
    state = {
        options: [],
        currValue: ""
    }
    componentDidMount(){
        axios({
            method: "GET",
            url: this.props.dataURL
        }).then(res => {
            const dataList = this.props.resProcessor(res);
            // returns a list of objects with value and name properties
            if(this.props.onPopulated){
                this.setState({options: dataList}, this.props.onPopulated);
            }else{
                this.setState({options: dataList});
            }
        }
            )
    }

    componentDidUpdate(prevProps, prevState){
        if(this.props.resetFlag && this.props.resetFlag != prevProps.resetFlag){
            this.setState({currValue: ""})
        }
    }

    render(){
        return(
            <select 
                value={this.state.currValue}
                id={this.props.ID}
                onChange={(evt) => this.props.handler(evt.target.value)}
                className={this.props.noCSS ? "" : "form-control"}
                name={this.props.name}
                >
                <option value="">-------</option>
                {this.state.options.map((opt, i) =>{
                    return(<option 
                                value={opt.value}
                                key={i}>{opt.name}</option>)
                })}
            </select>
        )
    }
}

AsyncSelect.propTypes = {
    dataURL: PropTypes.string.isRequired,
    resProcessor: PropTypes.func.isRequired,
    handler: PropTypes.func.isRequired,
}

export default AsyncSelect;