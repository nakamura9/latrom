import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import TransactionTable from './accounting/compound_transaction';
import CurrencyConverter from './accounting/currency/containers/root';
import GenericTable from './src/generic_list/containers/root'
import SelectWidget from './src/components/select';
const transactionTable = document.getElementById('transaction-table');
const currency = document.getElementById('currency-converter');
const accounts = document.getElementById('accounts-list');

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
                                handler={handler}
                                options={[
                                    {
                                        'value': '',
                                        'label': '------'
                                    },
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
                                options={[
                                    {
                                        'value': '',
                                        'label': '------'
                                    },
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
}

