import React, {Component} from 'react';
import { SearchableWidget, AsyncSelect } from '../../common';

/* fieldOrder - array of strings 
   insertHandler - function
   fields - array of objects
*/
class inputLine extends Component{
    state = {
        data: {
        },
        fetchField: null,
        selectedPk: null,
    }
    inputHandler = (evt) =>{
        let newData = {...this.state.data};

        newData[evt.target.name] = evt.target.value;
        this.setState({data: newData});
    }

    resetFields =() =>{
        let newData = {};
        let i = 0;
        for( i in this.props.fields){
            newData[this.props.fields[i].name] = "";
        }
        this.setState({data: newData});

    }

    componentDidMount =  () => {
        this.resetFields();
    }
    
    componentDidUpdate(prevProps, prevState) {
        if(this.state.selectedPk !==  prevState.selectedPk && 
                this.fetchField !== null){
            this.state.fetchField.dataGetter(
                    this, 
                    this.state.fetchField.name, 
                    this.state.selectedPk
                );
        }
    }

    insertHandler = () =>{
        //clear field values before passing data to parent
        // iterate over every
        if(this.props.hasLineTotal){
            console.log('has line total');
            let newData = {...this.state.data};
            newData['lineTotal'] = this.props.calculateTotal(this.state.data);
            this.props.insertHandler(newData);
            
        }else{
            this.props.insertHandler(this.state.data)
        }
        this.resetFields();
    }
    searchHandler = (name, value) =>{
        //for searchable widget and asyncwidget
        let newData = {...this.state.data};
        newData[name] = value;
        const pk = value.split('-')[0];
        this.setState({
            data: newData,
            selectedPk: parseInt(pk)
        });
    }

    asyncResProcessor = (res) =>{
        return res.data.map((item, i)=>(
            {
                value: item.id + '-' + item.name,
                name: item.name
            }
        ))
    }
    fieldSelector = (fieldIndex) =>{
        const field = this.props.fields[fieldIndex];
        
        switch(field.type){
            case 'fetch':
                if(!this.state.fetchField){
                    this.setState({fetchField: field})
                }
                return <span>{this.state.data[field.name]}</span>;
                break;
            case 'select':
                return <AsyncSelect 
                    handler={(val) => this.searchHandler(field.name, val)}
                    resProcessor={this.asyncResProcessor}
                    dataURL={field.url}/>
                break;
            case 'text':
                return <input 
                        type="text"
                        className="form-control"
                        onChange={this.inputHandler}
                        name={field.name}
                        value={this.state.data[field.name]}
                        />;    
                    break;
            case 'number':
                return <input 
                    type="number"
                    className="form-control"
                    onChange={this.inputHandler}
                    name={field.name}
                    value={this.state.data[field.name]}
                    />;
                break;
            case 'search': 
                return <SearchableWidget 
                    list={this.props.lines}
                    dataURL={field.url}
                    idField={field.idField}
                    canCreateNewItem={field.canCreateNewItem}
                    displayField={field.displayField}
                    newLink={field.newLink}
                    onSelect={(val) => this.searchHandler(field.name, val)}
                    onClear={() => this.searchHandler(field.name, "")}/>
                break;
            default:
                return null;
        }
    }
    render(){
        return(
                <tr className="bg-primary text-white"
                    style={{
                        borderTop: '2px solid white',
                    }}>
                    {this.props.fieldOrder.map((fieldName, i) =>(
                        <td key={i}>
                            <div style={{
                                paddingTop: '10px',
                                height: '70px',
                                margin: '0px auto'
                            }}>
                                {this.fieldSelector(i)}

                            </div>
                        </td>
                    ))}
                    <td colSpan={this.props.hasLineTotal 
                        ? 2
                        : 1}>
                        
                        <div style={{
                            paddingTop: '10px',
                            height: '70px',
                            margin: 'auto'
                        }}>
                        <button 
                            style={{float: 'right', marginRight: '10px'}}
                            className="btn"
                            onClick={this.insertHandler}>Insert</button>

                        </div>
                    </td>
                    
                </tr>
                    
        );
    }
}

export default inputLine;