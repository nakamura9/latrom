import React, {Component} from 'react';
import $ from 'jquery';

class Heading extends Component{
    //props of an array
    render(){
        var style = {
                backgroundColor: 'black',
                color: 'white',
                padding: '10px',
                borderLeft: '1px solid white'
            };
        return(
            <thead style={style}>
                <tr>
                <td style={{minWidth: '50px'}}></td>
                    {this.props.fields.map((field, index) =>(
                        <td style={style} key={index} > {field} </td>
                    ))}
                </tr>
            </thead>
        );
    }
}

class TableContent extends Component{
    render(){
        return(
            <tbody>
                {this.props.contents.map((row, index) =>(
                    <tr key={index}>
                        <td> 
                            <button type="button" 
                                    className="btn btn-danger"
                                    onClick={() => (this.props.removeHandler(index))}>
                                    <i className="fas fa-trash"></i>
                            </button>
                        </td>
                        {this.props.fields.map((field, i) =>(
                            <td key={i}>{row[field]}</td>
                        ))}
                        <td>
                            {this.props.subtotalHandler(row)}
                        </td>
                    </tr>
                ))}
            </tbody>
        ); 
    }
}


class AsyncSelect extends Component{
    constructor(props){
        super(props);
        this.state = {
            options: []
        }

    }

    componentDidMount(){
        $.ajax({
            method: "GET",
            url: this.props.url,
            data: {}
        }).then(res => {
                var i;
                var newState = this.state.options;
                for(i in res){
                    newState.push({
                        pk: res[i].code,
                        name: res[i].item_name
                    });
                }
                this.setState({options: newState});
            }
        );
    }
    
    render(){
        return(
            <select name="item_name" onChange={event => this.props.handleChange(event)} className="form-control">
                <option value="">-------</option>
                {this.state.options.map((option, index) =>
                (
                    <option key={index} value={option.pk}>{option.pk} - {option.name}</option>
                ))}
            </select>
        );
    }
}

export { TableContent, AsyncSelect, Heading};