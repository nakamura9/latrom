import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import TransactionTable from './accounting/compound_transaction';
import CurrencyConverter from './accounting/currency/containers/root';
import GenericTable from './src/generic_list/containers/root'
import SelectWidget from './src/components/select';

const transactionTable = document.getElementById('transaction-table');
const currency = document.getElementById('currency-converter');
const accounts = document.getElementById('accounts-list');
const entries = document.getElementById('entries-list');
const expenses = document.getElementById('expenses-list');
const bills = document.getElementById('bill-table');

if(transactionTable){
    ReactDOM.render(<TransactionTable />, transactionTable);
}else if(currency){
    ReactDOM.render(<CurrencyConverter />, currency);
}else if(accounts){
    ReactDOM.render(<GenericTable 
            fieldOrder={['name', 'description', 'code', 'balance', 'type', 'balance_sheet_category']}
            fieldDescriptions={['Name', 'Description', 'Code', 'Balance','Type', 
                'Balance Sheet Category']}
            formInputID='id_data'
            fields={[
                {
                    'name': 'name',
                    'type': 'text',
                    'width': '15',
                    'required': true
                },
                {
                    'name': 'description',
                    'type': 'text',
                    'width': '25',
                    'required': true
                },
                {
                    'name': 'code',
                    'type': 'number',
                    'width': '10',
                    'required': true
                },
                {
                    'name': 'balance',
                    'type': 'number',
                    'width': '10',
                    'required': true
                },
                {
                    'name': 'type',
                    'type': 'widget',
                    'width': '15',
                    'required': true,
                    'widgetCreator': (comp) =>{
                        const handler = (value) =>{
                            let newData = {...comp.state.data}
                            newData['type'] = value
                            comp.setState({'data': newData})
                        }
                        return(
                            <SelectWidget
                                resetFlag={comp.state.isReset}
                                handler={handler}
                                options={[
                                    
                                    {
                                        'label': 'Asset',
                                        'value': 'asset'
                                    },
                                    {
                                        'label': 'Liability',
                                        'value': 'liability'
                                    },
                                    {
                                        'label': 'Expense',
                                        'value': 'expense'
                                    },
                                    {
                                        'label': 'Income',
                                        'value': 'income'
                                    },
                                    {
                                        'label': 'Cost Of Sales',
                                        'value': 'cost-of-sales'
                                    },
                                    {
                                        'label': 'Equity',
                                        'value': 'equity'
                                    }
                                ]} />
                        )
                    }
                },
                {
                    'name': 'balance_sheet_category',
                    'type': 'widget',
                    'width': '15',
                    'required': true,
                    'widgetCreator': (comp) =>{
                        const handler = (value) =>{
                            let newData = {...comp.state.data};
                            newData['balance_sheet_category'] = value
                            comp.setState({data: newData})
                        }
                        return(
                            <SelectWidget
                                handler={handler}
                                resetFlag={comp.state.isReset}
                                options={[
                                    
                                    {
                                        'value':'current_assets',
                                        'label': 'Current Assets'
                                    },
                                    {
                                        'value':'current-liabilities',
                                        'label': 'Current Liabilities'
                                    },
                                    {
                                        'value':'long-term-assets',
                                        'label': 'Long Term Assets'
                                    },
                                    {
                                        'value':'long-term-liabilities',
                                        'label': 'Long Term Liabilities'
                                    },
                                    {
                                        'value':'equity',
                                        'label': 'Equity'
                                    },
                                    {
                                        'value':'not-included',
                                        'label': 'Not Included'
                                    },
                                ]} />
                        )
                    }
                },
            ]}
            />, accounts)
}else if(entries){
    ReactDOM.render(<GenericTable 
            fieldOrder={['date', 'memo', 'account', 'credit', 'debit']}
            fieldDescriptions={['Date', 'Memo', 'Account', 'Credit','Debit']}
            formInputID='id_data'
            fields={[
                {
                    'name': 'date',
                    'type': 'date',
                    'width': '15',
                    'required': true
                },
                {
                    'name': 'memo',
                    'type': 'text',
                    'width': '20',
                    'required': true
                },
                {
                    'name': 'account',
                    'type': 'search',
                    'width': '25',
                    'required': true,
                    'model': 'account',
                    'app': 'accounting',
                    'newLink': '/accounting/create-account',
                    url: '/accounting/api/account/', 
                    idField: 'id',
                    displayField: 'name'
                },
                {
                    'name': 'credit',
                    'type': 'number',
                    'width': '10',
                    'required': true
                },
                {
                    'name': 'debit',
                    'type': 'number',
                    'width': '10',
                    'required': true,
                },
            ]}
            />, entries)
}else if(expenses){
    ReactDOM.render(<GenericTable 
            fieldOrder={['date', 'description', 'category', 'amount']}
            fieldDescriptions={['Date', 'Description', 'Category', 'Amount']}
            formInputID='id_data'
            fields={[
                {
                    'name': 'date',
                    'type': 'date',
                    'width': '15',
                    'required': true
                },
                {
                    'name': 'description',
                    'type': 'text',
                    'width': '20',
                    'required': true
                },
                {
                    'name': 'category',
                    'type': 'widget',
                    'width': '15',
                    'required': true,
                    'widgetCreator': (comp) =>{
                        const handler = (value) =>{
                            let newData = {...comp.state.data};
                            newData['category'] = value
                            comp.setState({data: newData})
                        }
                        return(
                            <SelectWidget
                                resetFlag={comp.state.isReset}
                                handler={handler}
                                options={[{'value': 'Advertising', 'label': 'Advertising'}, {'value': 'Bank Service Charges', 'label': 'Bank Service Charges'}, {'value': 'Dues and Subscriptions', 'label': 'Dues and Subscriptions'}, {'value': 'Equipment Rental', 'label': 'Equipment Rental'}, {'value': 'Telephone', 'label': 'Telephone'}, {'value': 'Vehicles', 'label': 'Vehicles'}, {'value': 'Travel and Expenses', 'label': 'Travel and Expenses'}, {'value': 'Supplies', 
                                'label': 'Supplies'}, {'value': 'Salaries and Wages', 'label': 'Salaries and Wages'}, {'value': 'Rent', 'label': 'Rent'}, {'value': 'Payroll Taxes', 'label': 'Payroll Taxes'}, {'value': 'Legal and Accounting', 'label': 'Legal and Accounting'}, {'value': 'Insurance', 'label': 'Insurance'}, {'value': 'Office Expenses', 'label': 'Office Expenses'}, {'value': 'Carriage Outwards', 'label': 'Carriage Outwards'}, {'value': 'Other', 
                                'label': 'Other'}]} />
                        )
                    }
                },
                {
                    'name': 'amount',
                    'type': 'number',
                    'width': '10',
                    'required': true
                }
            ]}
            />, expenses)
}else if(bills){
    ReactDOM.render(<GenericTable 
            fieldOrder={['category', 'description', 'amount']}
            fieldDescriptions={['Expense Category', 'Memo', 'Amount']}
            formInputID='id_data'
            fields={[
                {
                    'name': 'category',
                    'type': 'widget',
                    'width': '30',
                    'required': true,
                    'widgetCreator': (comp) =>{
                        const handler = (value) =>{
                            let newData = {...comp.state.data};
                            newData['category'] = value
                            comp.setState({data: newData})
                        }
                        return(
                            <SelectWidget
                                handler={handler}
                                resetFlag={comp.state.isReset}
                                options={[{'value': 'Advertising', 'label': 'Advertising'}, {'value': 'Bank Service Charges', 'label': 'Bank Service Charges'}, {'value': 'Dues and Subscriptions', 'label': 'Dues and Subscriptions'}, {'value': 'Equipment Rental', 'label': 'Equipment Rental'}, {'value': 'Telephone', 'label': 'Telephone'}, {'value': 'Vehicles', 'label': 'Vehicles'}, {'value': 'Travel and Expenses', 'label': 'Travel and Expenses'}, {'value': 'Supplies', 
                                'label': 'Supplies'}, {'value': 'Salaries and Wages', 'label': 'Salaries and Wages'}, {'value': 'Rent', 'label': 'Rent'}, {'value': 'Payroll Taxes', 'label': 'Payroll Taxes'}, {'value': 'Legal and Accounting', 'label': 'Legal and Accounting'}, {'value': 'Insurance', 'label': 'Insurance'}, {'value': 'Office Expenses', 'label': 'Office Expenses'}, {'value': 'Carriage Outwards', 'label': 'Carriage Outwards'}, {'value': 'Other', 
                                'label': 'Other'}]} />
                        )
                    }
                },
                {
                    'name': 'description',
                    'type': 'text',
                    'width': '50',
                    'required': true
                },
                {
                    'name': 'amount',
                    'type': 'number',
                    'width': '20',
                    'required': true
                },
            ]}
            />, bills)
}

