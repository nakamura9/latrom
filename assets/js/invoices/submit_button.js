import React, {Component} from 'react';
import {DropdownButton, MenuItem} from 'react-bootstrap';
import $ from 'jquery';

export default class SubmitButton extends Component{
    injectStatus = (evt, status) => {
        $('input').attr({
            name: 'status',
            type: 'hidden',
            value: status
        }).appendTo('form');
    }
    render(){
        return(
            <DropdownButton
                title="Submit As..."
                id='submitAs'>
                <MenuItem
                    eventKey={1}
                    onClick={(evt) => this.injectStatus(evt, 'draft')}>
                    Draft
                </MenuItem>
                <MenuItem 
                    
                    onClick={(evt) => this.injectStatus(evt, 'quotation')}>
                    Quotation
                </MenuItem>
                <MenuItem 
                    onClick={(evt) => this.injectStatus(evt, 'invoice')}>
                    Invoice
                </MenuItem>
                <MenuItem 
                    onClick={(evt) => this.injectStatus(evt, 'sent')}>
                    Invoice and Send Email
                </MenuItem>
                <MenuItem 
                    onClick={(evt) => this.injectStatus(evt, 'paid')}>
                    Invoice and Apply Payment
                </MenuItem>
            </DropdownButton>
        );
    }
}