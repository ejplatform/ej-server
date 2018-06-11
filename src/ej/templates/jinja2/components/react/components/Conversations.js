import React, { Component } from 'react';
import Conversation from './Conversation';
import FullConversation from './FullConversation';
import config from '../config';
import util from 'util';

class Conversations extends Component {
  constructor(props) {
    super(props);
    this.state = {
      conversations: [],
      conversation: null
    };
  }

  componentDidMount() {
    fetch(`${config.host}/api/v1/conversations/?format=json`)
      .then(res => res.json())
      .then(
        (result) => {
          let slug = null;
          if (this.props.slug) {
            slug = this.props.slug;
          }
          if (slug) {
            result.results.forEach((conversation) => {
              if (conversation.slug === slug) {
                this.setState({ conversation });
              }
            });
          }
          else {
            this.setState({ conversations: result.results });
          }
        },
        (error) => {
          console.log(util.inspect(error));
        }
      )
  }

  render() {
    if (this.state.conversation) {
      return (<FullConversation conversation={this.state.conversation} />);
    }
    else if (this.state.conversations.length) {
      return (
        <div className="Conversations">
          <h1>Conversas Ativas</h1>
          <h2>Ver conversas ativas para dar sua opinião</h2>
          <ul>
          {this.state.conversations.map(conversation => (
            <li key={conversation.slug}>
              <Conversation conversation={conversation} />
            </li>
          ))}
          </ul>
        </div>
      );
    }
    else {
      return null;
    }
  }
}

export default Conversations;
