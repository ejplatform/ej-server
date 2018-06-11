import React, { Component } from 'react';
import FontAwesome from 'react-fontawesome';
import config from '../config';
import util from 'util';

class FullConversation extends Component {
  constructor(props) {
    super(props);
    this.state = {
      comment: null
    };
  }

  // FIXME: Not working due to a bug on the backend
  vote(value) {
    const { comment } = this.state;
    const user = this.getUser();

    if (comment && user) {
      const mapping = {
        agree: 1,
        skip: 0,
        disagree: -1
      };
      fetch(comment.links.vote + '/', {
        headers: {
          'accept': 'application/json',
          'content-type': 'application/json',
          'authorization': 'Token ' + user.token,
        },
        method: 'POST',
        body: JSON.stringify({ comment: comment.id, value: mapping[value] })
      })
      .then(res => res.json())
      .then(
        (result) => {
          this.loadComment();
        },
        (error) => {
          console.log(util.inspect(error));
        }
      );
      alert('Obrigado pelo seu voto!');
    }
  }

  loadComment() {
    fetch(`${config.host}/api/v1/conversations/${this.props.conversation.slug}/random_comment/?format=json`, { credentials: 'include' })
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({ comment: result });
        },
        (error) => {
          console.log(util.inspect(error));
        }
      )
  }

  getUser() {
    let user = null;
    if (window.EJ) {
      user = window.EJ.currentUser;
    }
    return user;
  }

  componentDidMount() {
    this.loadComment();
  }

  render() {
    const { conversation } = this.props;
    const { comment } = this.state;

    return (
      <div className="FullConversation">
        <div className="FullConversation-cover">
          <h1>{conversation.title}</h1>
          <ul className="FullConversation-statistics">
            <li>{conversation.statistics.comments.total} comentários</li>
            <li>{conversation.statistics.votes.total} votos</li>
          </ul>
        </div>
        <div className="FullConversation-arrow"></div>
        <ul className="FullConversation-statisticsBottom">
          <li>
            <div>categoria:</div>
            <div>{conversation.category_name}</div>
          </li>
          <li>veja mais<br />categorias</li>
        </ul>
        <div className="FullConversation-header">
          <h1>Opiniões da comunidade</h1>
          <p>Interaja com as opiniões da comunidade selecionando um dos botões de opção.</p>
        </div>
        { comment && comment.id ?
        <div className="FullConversation-comment">
          <div className="FullConversation-comment-user">
            <FontAwesome name="user" /> <span>{ comment && comment.author_name ? comment.author_name : 'Nenhum' }</span>
          </div>
          <p>{ comment && comment.content ? comment.content : 'Nenhum' }</p>
          <ul className="FullConversation-votes">
            <li>
              <button onClick={this.vote.bind(this, 'agree')}>
                <FontAwesome name="check" />
              </button>
              <span>Concorda</span>
            </li>
            <li>
              <button onClick={this.vote.bind(this, 'skip')}>
                <FontAwesome name="arrow-right" />
              </button>
              <span>Pular</span>
            </li>
            <li>
              <button onClick={this.vote.bind(this, 'disagree')}>
                <FontAwesome name="times" />
              </button>
              <span>Discorda</span>
            </li>
          </ul>
        </div>
        : <div className="FullConversation-comment"><p>Nenhum comentário para votar.</p></div> }
      </div>
    );
  }
}

export default FullConversation;
