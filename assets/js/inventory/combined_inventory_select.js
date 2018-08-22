class SearchableWidget extends Component {
    //currValue is whats being typed, selected is the value validated
    state = {
        items: [],
        choices: [],
        currValue: "",
        selectedValue: ""
    }

    componentDidMount(){
        axios({
            method: "GET",
            url: '/api/inventory-product'
        }).then(res => {
            let newChoices = res.data.map((item) =>{
                return(item[this.props.idField] + " - " + item[this.props.displayField])
            });

            this.setState({
                items: res.data,
                choices: newChoices
            });
        })
    }

    handleChange = (evt) => {
        let selectedValue = "";
        let index = this.state.choices.indexOf(evt.target.value);
        
        if(index !== -1){
            selectedValue = evt.target.value;

        }
        this.setState({
            currValue: evt.target.value,
            selectedValue: selectedValue
        });
        if(index !== -1){
            this.props.onSelect(evt.target.value);
        }
    }
    render(){
        let rendered;
        if(this.state.selectedValue === ""){
            rendered = (
                <input 
                    type="text"
                    className="form-control"
                    value={this.state.currValue}
                    onChange={this.handleChange}
                    placeholder="Select item..."
                    list="id_list"/>
            )
        }else{
            rendered = (
                <div style={{width:'100%'}}>
                    <span>{this.state.selectedValue}</span>
                    <span style={{float:'right'}}>
                        <button 
                            className="btn btn-secondary"
                            onClick={() =>{
                                this.setState({
                                    selectedValue: "",
                                    currValue: ""
                                });
                                this.props.onClear();
                            }}>
                            <i className="fas fa-times"></i>
                        </button>
                    </span>
                </div>
            )
        }
        return(
            <div>
                {rendered}   
                <datalist id="id_list">
                    {this.state.items.map((item, i) => {
                        //always display id and display field
                        return(<option key={i} >
                                {item[this.props.idField]} - {item[this.props.displayField]}
                            </option>)
                    })}
                    
                </datalist>
            </div>
        );
    }
}