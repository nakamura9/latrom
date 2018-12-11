import React, {Component} from 'react';
import AsyncSelect from '../../../src/components/async_select';

class RateWidget extends Component{
    state = {
        unit: null,
        rate: null
    }

    unitHandler = (val) =>{
        this.setState({unit: val});
    }

    rateHandler = (val) =>{
        this.setState({rate: val});
    }
    render(){
        return(
        <div>
            <fieldset>
                <legend>Rate</legend>
                <AsyncSelect
                    name="process_rate_unit"
                    dataURL="/inventory/api/unit/"
                    handler={this.unitHandler}
                    resProcessor={(res) => {
                        return res.data.map((unit) =>({
                            name: unit.name,
                            value: unit.id
                        }))
                    }} />
                <select 
                    className="form-control"                    
                    onChange={this.rateHandler}
                    name="process_rate_unit_time"
                    style={{display: 'inline'}}>
                    <option value={0}>Per Second</option>
                    <option value={1}>Per Minute</option>
                    <option value={2}>Per Hour</option>
                </select>
                <button 
                    type="button"
                    className="btn btn-info"
                    onClick={() => this.props.clickHandler(this.state)}>
                    Set
                </button>
            </fieldset>
        </div>
        )
    }
}

export default RateWidget;