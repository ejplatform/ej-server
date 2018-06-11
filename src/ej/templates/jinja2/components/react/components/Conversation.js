import React, { Component } from 'react';
import FontAwesome from 'react-fontawesome';

class Conversation extends Component {
  // FIXME: API must return conversation.category_slug
  render() {
    const { conversation } = this.props;
    const link = `/conversations/${conversation.category_name.toLowerCase()}/${conversation.slug}`;
    
    return (
      <div className="Conversation">
        <div className="Conversation-cover">
          <h3>{conversation.title}</h3>
          <p>Assunto: {conversation.category_name}</p>
        </div>
        <div className="Conversation-actions">
          { conversation.statistics ?
          <ul className="Conversation-statistics">
            <li>{conversation.statistics.comments.total} comentários</li>
            <li>{conversation.statistics.votes.total} votos</li>
          </ul> : null }
          <a href={link} className="Conversation-button">Participar <FontAwesome name="comments" style={{ marginLeft: 7 }} /></a>
        </div>
      </div>
    );
  }
}

export default Conversation;
