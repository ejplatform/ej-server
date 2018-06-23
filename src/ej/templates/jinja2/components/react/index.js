import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import util from 'util';

window.renderComponent = function(componentName, params) {
  ReactDOM.render(<App component={componentName} {...params} />, document.getElementById('React-Root-' + componentName));
}

const event = new CustomEvent('ReactLoaded');
document.dispatchEvent(event);
