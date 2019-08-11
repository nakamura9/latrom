import React from 'react';
import styles from '../styles.css';

const bg = (props) =>{
    return(
        <div className={styles.timelineBg}>
            <div className={styles.timelineBgLeft}>
                <div className={styles.timelineLine}></div>
            </div>
            <div className={styles.timelineBgRight}></div>
        </div>
    )
}

export default bg;