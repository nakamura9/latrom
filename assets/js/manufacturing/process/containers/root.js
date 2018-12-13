import React, {Component} from 'react';
import GenericTable from '../../../src/generic_list/containers/root';
import ProcessDetails from '../components/process_details';

class ProcessRoot extends Component{
    render(){
        return(
            <div className="container">
                <h3>Process Creation App</h3>
                <hr />
                <div className="row">
                <div className="col-sm-4">
                <h4>Process Details</h4>
                <ProcessDetails />
                </div>
                <div className="col-sm-8">
                    <div>
                        <h4>Inputs</h4>
                        <h5>Bill of Materials <button 
                            className="btn btn-info"
                            onClick={() => {
                                $('#popup-frame').attr('src', "/inventory/raw-material-create/");
                                var modal = document.getElementById('id-my-modal');
                                    modal.style.display = 'block';
                            }}>Create New</button></h5>
                        <hr />
                        <GenericTable 
                            hasLineTotal={false}
                            formInputID="id_materials"
                            hasTotal={false}
                            fieldOrder={['raw material','unit']}
                            fields={[
                                {
                                    name: 'raw material',
                                    type: 'search',
                                    width: 40,
                                    required: true,
                                    url: '/inventory/api/raw-material/',
                                    idField: 'id',
                                    displayField: 'name'
                                },
                                {
                                    name: 'unit',
                                    type: 'select',
                                    url: '/inventory/api/unit/',
                                    asyncResPRocessor: function(res){
                                        return(res.data.map((item)=>({
                                            value: item.id,
                                            name: item.name
                                        })   
                                        ))
                                    },
                                    width: 15,
                                    required: true
                                }
                            ]}/>
                        <hr />
                        <h5>Process Equipment </h5>
                        <hr />
                        <h6>Machine(s) <button 
                        className="btn btn-info"
                        onClick={() => {
                            $('#popup-frame').attr('src', "/manufacturing/process-machine/create");
                            var modal = document.getElementById('id-my-modal');
                                modal.style.display = 'block';
                        }}>Create New</button></h6>
                        <GenericTable 
                            hasLineTotal={false}
                            formInputID="id_equipment"
                            hasTotal={false}
                            fieldOrder={['machine']}
                            fields={[
                                {
                                    name: 'machine',
                                    type: 'search',
                                    width: 40,
                                    required: true,
                                    url: '/manufacturing/api/process-machine/',
                                    idField: 'id',
                                    displayField: 'name'
                                }
                            ]}/>
                        <hr />
                    </div>
                    <div>
                        <h4>Outputs</h4>
                        <hr />
                        <h5>Products <button 
                        className="btn btn-info"
                        onClick={() => {
                            $('#popup-frame').attr('src', "/manufacturing/process-product/create");
                            var modal = document.getElementById('id-my-modal');
                                modal.style.display = 'block';
                        }}>Create New</button></h5>
                        <GenericTable 
                            hasLineTotal={false}
                            formInputID="id_products"
                            hasTotal={false}
                            fieldOrder={['process product']}
                            fields={[
                                {
                                    name: 'process product',
                                    type: 'search',
                                    width: 40,
                                    required: true,
                                    url: '/manufacturing/api/process-product/',
                                    idField: 'id',
                                    displayField: 'name'
                                }
                            ]}/>
                        <hr />
                    </div>                
                </div>
                </div>
                <hr />                
            </div>
        )
    }
}

export default ProcessRoot;