import React, {Component} from 'react';

class Warehouse extends Component {
    render(){
        return(
            <div className="container">
                <div className="col-9">
                    <div>
                        this.state.levelOne.map((level) =>{
                            return(<LevelTwo data={level} />)
                        })
                    
                    </div>
                </div>
                <div className="col-3"></div>
            </div>
        )
    }
}