import React from 'react';
import styles from '../styles.css';

const bg = (props) =>{
    const height = 200 + (props.cards * 100);
    console.log(height)
    return(
        <div className={styles.timelineBg}>
            <div className={styles.timelineBgLeft}>
                <div className={styles.timelineLine}
                    style={{
                        height: `${height}px`
                    }}></div>
            </div>
            <div className={styles.timelineBgRight}></div>
        </div>
    )
}

export default bg;