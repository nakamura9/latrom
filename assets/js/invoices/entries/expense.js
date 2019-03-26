import React, {Component} from 'react';
import SearchableWidget from '../../src/components/searchable_widget';


const ExpenseEntry = (props) => {
    if(props.billables.length === 0){
            return(
                <div>
                    <center>
                        <h6>The selected customer has no billable expenses</h6>
                        <button 
                        style={{width:"100%"}}
                        className="btn"
                        onClick={() => window.open(
                            '/accounting/expense/create' ,'popup','width=900,height=480')}>
                        Add Expense <i className="fas fa-plus"></i>
                    </button>
                    </center>
                </div>
            )
        }else{
            return(
                <div style={{width:"100%"}}>
                    <SearchableWidget 
                        dataURL={`/accounting/api/expense/customer/${document.getElementById('id_customer').value}`}
                        onSelect={props.handler}
                        onClear={props.handler}
                        idField="id"
                        displayField="description"
                    />
                    
                </div>
            )
        }
};

export default ExpenseEntry;