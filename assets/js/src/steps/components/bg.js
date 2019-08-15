import React from 'react';
import styles from '../steps.css';

const stepsBg =(props) =>{
    return(
        <div className={styles.stepsBg}>
            <div className={styles.stepsBgLeft}>
                <div className={styles.stepsLine}></div>
            </div>
            <div className={styles.stepsBgRight}></div>
        </div>
    )
}

export default stepsBg;