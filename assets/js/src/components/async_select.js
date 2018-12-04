import React, {Component} from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';

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
            this.setState({options: dataList});
        }
            )
    }
    render(){
        return(
            <select 
                onChange={(evt) => this.props.handler(evt.target.value)}
                className="form-control">
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