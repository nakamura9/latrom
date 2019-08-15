import React from 'react';
import styles from '../steps.css';
import StepPoint from './point';

const step = (props) =>{
    return(
        <div className={styles.step}>
            <div className={styles.stepLeft}>
                <StepPoint checked={props.checked}/>
            </div>
            <div className={styles.stepRight}>
                <p>{props.name}</p>
            </div>
        </div>
    )
}

export default step;