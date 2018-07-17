import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';

class InventoryChecker extends Component {
    constructor(props){
        super(props);
        this.state = {
            items : [],
            warehouse: "",
            nextPage: 2,
            pages: 1
        }
    }

    componentDidMount(){
        let url = window.location.href;
        let url_elements = url.split('/');
        console.log(url_elements);
        let warehouse = url_elements[url_elements.length - 1]
        this.setState({
            warehouse: warehouse,
        });
        console.log(warehouse);
        $.ajax({
            'url': '/inventory/api/warehouse-items/'+ warehouse,
            'method': 'GET',
        }).then(res => {
            console.log(res);
            this.setState({
                items: res.results,
                pages:res.count
            });
        });
    }

    nextPage(evt){
        if(this.state.nextPage > this.state.pages){
            alert('Inventory is finished');
            evt.target.disabled =true;
        }else{
            this.setState({items: []});
            $.ajax({
                'url': '/inventory/api/warehouse-items/'+ this.state.warehouse,
                'method': 'GET',
                data: {
                    page: this.state.nextPage
                }
    
            }).then(res => {
                this.setState({
                    items: res.results,
                    nextPage: this.state.nextPage + 1
                });
            });
        }
        
    }
    render(){
        return(
            <div>
            <table className="table">
            <thead>
                <tr className="bg-primary">
                    <th></th>
                    <th>Item</th>
                    <th>Recorded Quantity</th>
                    <th>Measured Quantity</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>{
                this.state.items.length === 0
                ? <tr>
                    <td colSpan={4} style={{textAlign:'center'}}><b>Select a populated warehouse</b></td>
                  </tr>
                : this.state.items.map((item, i) => (
                    <WareHouseItem data={item} 
                    key={i}/>
                ))
            }
            </tbody>
        </table>
        <button className="btn btn-primary" 
            style={{float:"right"}}
            onClick={this.nextPage.bind(this)}>Next</button>
        </div>
        );
    }
}

class WareHouseItem extends Component{
    constructor(props){
        super(props);
        this.state = {
            value: this.props.data.quantity,
            verified: false
        }
    }

    updateVal(evt){
        //do other validation tasks
        this.setState({value: parseFloat(evt.target.value)});
    }
    validate(evt){
        if(this.state.value === this.props.data.quantity){
            this.setState({verified: true});
        }else{
            this.createAdjustment();
        }
    }
    createAdjustment(){
        let note = prompt('Create Acompanying Note:');
        let url = window.location.href;
        let url_elements = url.split('/');
        $.ajax({
            'url': '/inventory/api/stock-adjustment/',
            'method': 'POST',
            'data': {
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                warehouse_item: this.props.data.id,
                adjustment: this.props.data.quantity - this.state.value,
                note: note,
                inventory_check: url_elements[url_elements.length-2]
            }
        }).then(() =>{
            this.setState({'verified': true});
        })
    }

    render(){
        return(
            <tr>
                <td>
                    <input type="checkbox" checked={this.state.verified} />
                </td>
                <td>{this.props.data.item.item_name}</td>
                <td>{this.props.data.quantity}</td>
                <td>
                    <input type="number"
                        className="form-control"
                        onChange={this.updateVal.bind(this)}
                        defaultValue={this.props.data.quantity}/>
                </td>

                <td>
                    <button className="btn btn-primary" 
                        onClick={this.validate.bind(this)}
                        disabled={this.state.verified}>Verify</button>
                        
                </td>
            </tr>
        );
    }
}

ReactDOM.render(
    <InventoryChecker />, document.getElementById('inventory-checker')
)