import React, {Component} from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import $ from 'jquery';

export const Aux = (props) => props.children;

const DeleteButton = (props) => {
        return(
            <button
                className="btn btn-danger btn-sm"
                type="button"
                onClick={() => (props.handler(props.index))}>
                <i className="fas fa-trash"></i>
            </button>
        );
    }

DeleteButton.propTypes = {
    handler: PropTypes.func.isRequired,
    index: PropTypes.number.isRequired
}

class Totals extends Component{
    state = {
        taxObj: null,
        tax: 0.00,
        subtotal: 0.00,
        total: 0.00
    }

    setTaxFromForm = (evt) =>{
        axios({
            method: "GET",
            url: "/accounting/api/tax/" + evt.target.value
        }).then(res =>{
            this.setState({taxObj: res.data});
        })

    }
    componentDidMount(){
        //get sales tax
        //look for tax in page if not found get global tax
        $('#id_tax').on('change', this.setTaxFromForm);

        axios({
            method: "GET",
            url: "/invoicing/api/config/1"
        }).then(res =>{
            this.setState({taxObj: res.data.sales_tax})
        })
    }
    componentDidUpdate(prevProps, prevState){
        if(prevProps.list !== this.props.list || prevState.taxObj !== this.state.taxObj){
            //update totals 
            let subtotal = this.props.list.reduce(this.props.subtotalReducer, 0);
            
            let taxAmount;
            if(this.state.taxObj){
                taxAmount = subtotal * (this.state.taxObj.rate / 100);
            }else{
                taxAmount = 0.0;
            }
            let total = subtotal + taxAmount;
            this.setState({
                subtotal : subtotal,
                tax : taxAmount,
                total : total
            });
        }
    }
    render(){
        let contents;
        if(this.state.tax === null){
            contents = (
                <tfoot>
                    <tr>
                        <th colSpan={this.props.span - 1}>Total</th>
                        <td>{this.state.total}</td>
                    </tr>
                </tfoot>
            )
        }else{
            contents = (
                <tfoot>    
                    <tr>
                            <th colSpan={this.props.span - 1}>Subtotal</th>
                            <td>{this.state.subtotal.toFixed(2)}</td>
                        </tr>
                        <tr>
                            <th colSpan={this.props.span - 1}>Tax</th>
                            <td>{this.state.tax.toFixed(2)}</td>
                        </tr>
                        <tr>
                            <th colSpan={this.props.span - 1}>Total</th>
                            <td>{this.state.total.toFixed(2)}</td>
                        </tr>
                </tfoot>
                )
        }
        return(contents);
    }
}

Totals.propTypes = {
    span: PropTypes.number.isRequired,
    list: PropTypes.array.isRequired,
    subtotalReducer: PropTypes.func.isRequired
}


class AsyncSelect extends Component{
    state = {
        options: [],
        selected: ""
    }
    componentDidMount(){
        axios({
            method: "GET",
            url: this.props.dataURL
        }).then(res => {
            const dataList = this.props.resProcessor(res);
            this.setState({options: dataList});
        }
            )
    }

    selectHandler = (evt) =>{
        const val = evt.target.value
        this.setState({
            'selected': val
        }, () =>this.props.handler(val));
        
    }

    componentDidUpdate(prevProps, prevState) {
        if(this.props.resetFlag && this.props.resetFlag != prevProps.resetFlag){
            this.setState({'selected': ''})
        }
    }
    render(){
        return(
            <select
                selected={this.state.selected} 
                onChange={this.selectHandler}
                className="form-control">
                <option selected={this.state.selected==""} value="">-------</option>
                {this.state.options.map((opt, i) =>{
                    return(<option 
                                value={opt.value}
                                key={i}>{opt.name.replace('-', '_')}</option>)
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

class ImgPreview extends Component{
    state = {
        url: ''
    }

    componentDidMount(){
        axios({
            url: this.props.url,
            method: 'GET'
        }).then(res =>{
            this.setState({url: res.data})
        })
        const input = document.getElementById(this.props.inputID);
        input.addEventListener('change', () => this.renderImg(input))
        
    }

    renderImg =(input) =>{
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = (e) => {
                this.setState({url: e.target.result})
            }

            reader.readAsDataURL(input.files[0]);
        }
    }
    render(){
        return (
            <div style={{
                border: "1px solid #ddd",
                borderRadius: "5px",
                padding: "10px",
                display: "flex",
                justifyContent: "center"
            }}>
                {this.state.url === ''
                ? <div >
                    <h6>Select An image</h6>
                    <i className="fas fa-image" style={{fontSize: "12rem"}}></i>
                </div> 
                : <img width={300} height={200} src={this.state.url} />
                 }
            </div>
        )
    }
}
//SearchableWidget
export {DeleteButton, Totals, AsyncSelect, ImgPreview};