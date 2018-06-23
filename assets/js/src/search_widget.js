import React, {Component} from 'react';

class SearchWidget extends Component {
    constructor(props){
        //takes a json url as props and 
        //returns a list of selectable values
        super(props);
    
        this.state = {
            options: [],
            inputVal: "",
            selected: false
        }
    }

    addSelected(){
        this.setState({selected: this.state.inputVal});
        this.props.handler(this.state.inputVal);
    }

    removeSelected(id){
        this.setState({selected: ""});
    }

    componentDidMount(){
        $.ajax({
            url: this.props.url,
            data: {},
            method: "GET"
        }).then(res => {
            this.setState({options: res});
        });
        if(this.props.populated){
            this.props.populatedHandler(this);
        }
    }

    handleChange(val){
        this.setState({inputVal: val});
        
    }

    render() {
        const selectedStyle = {
            border: "1px solid blue",
            borderRadius: "5px",
            padding: "5px",
            margin: "5px",
            minHeight: "45px"
        };
        return(
            <div>
                    { this.state.selected ? 
                    <div style={selectedStyle}>
                        <span className="pull-left"><h5>{this.state.inputVal}</h5></span>
                        <span className="pull-right">
                            <button type="button" className="btn btn-default" onClick={this.removeSelected.bind(this)}>
                            <span className="fas fa-trash"></span>
                            </button>
                        </span>
                    </div>
                        : 
                    <div className="input-group">
                        <input id="search-id-input" placeholder="Search..." className="form-control" type="text" list="dlist" onChange={event => this.handleChange(event.target.value)} />
                        <span className="input-group-btn">
                            <button type="button" className="btn btn-primary" onClick={this.addSelected.bind(this)}>
                            <i className="fas fa-plus"></i>
                            </button>
                        </span>
                    </div>}
                    <datalist id="dlist">
                    {this.state.options.map((result, index) =>(
                        <option key={index}>{result.id} - {result.first_name} {result.last_name}</option>
                    ))
                }
                </datalist>
            </div>
        );
    }
}


export default SearchWidget;