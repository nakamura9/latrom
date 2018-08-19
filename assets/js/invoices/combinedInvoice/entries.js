import React from 'react';
import {SearchableWidget} from '../../src/common';

const inlineStyles = {
    display: "inline",
    float: "left"
};

const ServiceEntry = (props) => {
    return(
        <div>
            <div style={{...inlineStyles, width:"70%"}}>
                <SearchableWidget 
                    dataURL="/services/api/service/"
                    displayField="name"
                    idField="id"
                    onSelect={props.onSelect}
                    onClear={props.onClear} />
            </div>
            <div style={{...inlineStyles, width:"30%"}}>
                <input 
                    type="number"
                    placeholder="Hours..."
                    className="form-control"
                    onChange={props.onChangeHours}/>
            </div>
        </div>
    )
};

const ProductEntry = (props) => {
    return(
        <div>
            <div style={{...inlineStyles, width:"70%"}}>
                <SearchableWidget 
                    dataURL="/inventory/api/product/"
                    displayField="item_name"
                    idField="code"
                    onSelect={props.onSelect}
                    onClear={props.onClear} />
            </div>
            <div style={{...inlineStyles, width:"30%"}}>
                <input 
                    type="number"
                    placeholder="Quantity..."
                    className="form-control"
                    onChange={props.onChangeQuantity}/>
            </div>
        </div>
        )
};

const BillableEntry = (props) => {
    if(props.billables.length === 0){
            return(
                <div>
                    <center>
                        <h6>The selected customer has no billables</h6>
                    </center>
                </div>
            )
        }else{
            return(
                <div style={{width:"100%"}}>
                    <input 
                        type="text"
                        className="form-control"
                        list="billable_datalist"
                        placeholder="Select Billable Expense..."
                        onChange={props.inputHandler} />
                    <datalist id="billable_datalist">
                        {props.billables.map((billable, i)=>(
                            <option key={i}>
                                {billable.id + '-' + billable.description}
                            </option>
                        ))}
                    </datalist>
                </div>
            )
        }
};

export {ServiceEntry, BillableEntry, ProductEntry};