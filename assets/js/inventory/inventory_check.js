import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';

export default class InventoryChecker extends Component {
    state = {
            items : [],
            adjustments: [],
            warehouse: "",
            nextPage: 2,
            pages: 1
        }
    
    componentDidMount(){
        let url = window.location.href;
        let url_elements = url.split('/');
        let warehouse = url_elements[url_elements.length - 1]
        this.setState({
            warehouse: warehouse,
        });
        $.ajax({
            'url': '/inventory/api/warehouse-items/'+ warehouse,
            'method': 'GET',
        }).then(res => {
            this.setState({
                items: res.results,
                pages:res.count
            });
        });
        $('<input>').attr({
            type: 'hidden',
            name: 'adjustments',
            value: encodeURIComponent(JSON.stringify([])),
            id: 'id_adjustments'
        }).appendTo('form');
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

    updateForm = () =>{
        $('#id_adjustments').val(
            encodeURIComponent(
                JSON.stringify(this.state.adjustments)
            ));
    }

    adjustInventory = (data) => {
        let newAdjustments = [...this.state.adjustments];
        newAdjustments.push(data);
        this.setState({adjustments: newAdjustments}, this.updateForm);
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
                    <WareHouseItem 
                        data={item} 
                        key={i}
                        adjust={this.adjustInventory}/>
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
        this.props.adjust({
            warehouse_item: this.props.data.id,
            adjustment: this.props.data.quantity - this.state.value,
            note: note,
        })
        this.setState({'verified': true})

    }

    render(){
        let name = null;

        if(this.props.data.item_type === 1){
            name = this.props.data.product.name;
        }else if(this.props.data.item_type === 2){
            name = this.props.data.consumable.name;            
        }else if (this.props.data.item_type === 3){
            name = this.props.data.equipment.name;
        }

        return(
            <tr>
                <td>
                    <input type="checkbox" checked={this.state.verified} />
                </td>
                <td>{name}</td>
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

