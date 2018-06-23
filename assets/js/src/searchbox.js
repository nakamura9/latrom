import React, {Component} from 'react';

class SearchBox extends Component {
    constructor(props){
        super(props);
        this.state = {
            items: [],
            inputVal: "",
            results: ["caleb", "kandoro"]
        }
    }


    addSelected(){
        this.setState({items: this.state.items.concat({
            id: this.state.items.length, 
            name: this.state.inputVal})
        });
    }

    removeSelected(id){
        var newState = this.state;
        var index = newState.items.findIndex(a => a.id === id);

        if (index === -1) return;
        newState.items.splice(index, 1)
        
        this.setState(newState);
    }

    handleChange(val){
        this.setState({inputVal: val});
        
        // put code for retrieving results from a server
        this.setState({results: this.state.results.concat("awesome!")});
    }

    render() {

        const styles = {
            maxWidth: this.props.width,
            minHeight: "100px",
            padding: "5px",
            margin: "5px"
        }

        return(
            <div style={styles} className="bg-info" >
                <div className="input-group">
                    <input id="id-input" placeholder="Search..." className="form-control" type="text" list="dlist" onChange={event => this.handleChange(event.target.value)}/>
                    <span className="input-group-btn">
                    <button type="button" className="btn btn-primary" onClick={this.addSelected.bind(this)}>
                    <i class="fas fa-plus"></i>
                    </button>
                    </span>
                </div>               
                
                <datalist id="dlist">
                    {this.state.results.map((result, index) =>(
                        <option key={index}>{result}</option>
                    ))
                }
                </datalist>
                
                <div id="selected" style={{minHeight: "50px"}}>
                    {this.state.items.map((item, index) => (
                        <Selected key={index} id={item.id} val={item.name} rm={this.removeSelected.bind(this)} width={this.props.width -10} />
                    ))
                }
                </div>
            </div>
        );
    }
}

class Selected extends Component{
    
    remove(){
        this.props.rm(this);
    }

    render(){
        const styles = {
            padding: "5px",
            borderRadius: "5px",
            margin: "5px",
            border: "1px solid blue",
            minHeight: "45px"
            
        };

        return(
        <div style={styles}>
            <span style={{float:"left"}}>
                {this.props.val}
            </span>
            <span style={{float:"right"}}>
                <button type="button" className="btn btn-danger" onClick={() => this.props.rm(this.props.id)}>
                <i class="fas fa-trash"></i>
                </button>
            </span>
            
        </div>
        );
    }
}

export default SearchBox;