import React, {Component} from 'react';
import PropTypes from 'prop-types';

export const Aux = (props) => props.children;

const DeleteButton = (props) => {
        return(
            <button
                className="btn btn-danger"
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

export default DeleteButton;