import React, { Component } from 'react';
import Conversations from './components/Conversations';
import config from './config';
import util from 'util';

class App extends Component {
  componentDidMount() {
    fetch(`${config.host}/api/v1/users/me/?format=json`, { credentials: 'include' })
      .then(res => res.json())
      .then(
        (result) => {
          window.EJ = window.EJ || {};
          window.EJ.currentUser = result;
          this.forceUpdate();
        },
        (error) => {
          console.log(util.inspect(error));
        }
      )
  }

  render() {
    let component = null;
    switch (this.props.component) {
      case 'conversation_list':
        component = <Conversations />;
        break;
      case 'conversation':
        component = <Conversations slug={this.props.slug} />;
        break;
      default:
        component = null;
        break;
    };

    return (
      <div className="App">
        {component}
      </div>
    );
  }
}

export default App;
