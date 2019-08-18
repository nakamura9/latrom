import React from 'react';
import styles from '../steps.css';

const stepsPoint = (props) =>{
    return(
        <div className="stepPoint" style={{
            backgroundColor: props.checked ? '#00ff7b': 'white'
        }}>
            <i className="fas fa-check"></i>
        </div>
    )
}

export default stepsPoint;