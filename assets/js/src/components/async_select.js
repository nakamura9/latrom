import React, {Component} from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
/**
 * props 
 * dataURL - string with the data that populates the form
 * name - string that sets the name attribute in the select 
 * resProcessor - a function that takes the axios data and returns an array of 
 *                  value name objects
 * onPopulated - optional attr that provides an initial value of the form
 * handler - the function that is called when the select is changed.
 */


class AsyncSelect extends Component{
    state = {
        options: []
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
    render(){
        return(
            <select 
                onChange={(evt) => this.props.handler(evt.target.value)}
                className="form-control"
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