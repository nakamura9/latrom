import React, {Component} from 'react';

class ErrorBoundary extends Component{
    state = {
        hasError: false
    }
    componentDidCatch(error, info){
        console.log(error)
        console.log(info)
        this.setState({hasError: true});
    }

    render(){
        if (this.state.hasError){
            return <h3>Something went wrong</h3>
        }else{
            return this.props.children;
        }
    }
}

export default ErrorBoundary;