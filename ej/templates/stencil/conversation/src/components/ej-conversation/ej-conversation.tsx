import { Component, State } from '@stencil/core';
import { fetchConversation, fetchRandomComent, login, saveVote } from '../../global/http-service';
import { ConversationModel, CommentModel, VoteModel } from '../../global/interfaces';


@Component({
  tag: 'ej-conversation',
  styleUrl: 'ej-conversation.scss',
  shadow: true
})
export class Conversation {

  @State() conversation: ConversationModel;
  @State() comment: CommentModel;

  async componentDidLoad() {
    
    this.login('leandronunes', 'leandro12');
    this.setUpConversation();
  }

  async login(username, password) {
    try {
      const token = await login(username, password);
      localStorage.setItem('token', JSON.stringify(token.key));
    }
    catch (err) {
      console.log(err);
    }
  }

  async setUpConversation() {
    try {
      this.conversation = await fetchConversation();
      this.setUpRandomComment();
    }
    catch (err) {
      console.log(err);
    }
  }

  async setUpRandomComment() {
    try {
      this.comment = await fetchRandomComent(this.conversation.slug);
    }
    catch (err) {
      console.log(err);
    }
  }

  async agree(comment: CommentModel) {
    console.log('metodo agree', comment);
    try {
      await saveVote(comment, VoteModel.AGREE);
      console.log('agreeeeeeeeeeeeeeeeeeeeeeee');

    }
    catch (err) {
      console.log(err);
    }
  }

  async skip(comment: CommentModel) {
    console.log('metodo skip', comment);
    try {
      await saveVote(comment, VoteModel.PASS);
      console.log('skippppppppppppppppppppp');

    }
    catch (err) {
      console.log(err);
    }
  }

  async disagree(comment: CommentModel) {
    console.log('metodo disagree', comment);
    try {
      await saveVote(comment, VoteModel.DISAGREE);
      console.log('disssssssssssssssssssssssssssagree');

    }
    catch (err) {
      console.log(err);
    }
  }

  render() {
    if (this.conversation) {
      return (
        <div class='ej-conversation'>
          <div class="ConversationDetail">
            <div class="ConversationDetail-banner">
              <h1>{this.conversation.title}</h1>
              <ul class="ConversationDetail-statistics">
                <li>{this.conversation.statistics.comments.total}</li>
                <li>{this.conversation.statistics.votes.total}</li>
              </ul>
            </div>
            <div class="ConversationDetail-arrow"></div>

            <ul class="ConversationDetail-statisticsBottom">
              <li>
                <div>Categoria</div>
                <div>{this.conversation.category_name}</div>
              </li>
              <li>veja mais categorias</li>
            </ul>
            <div class="ConversationDetail-header">
              <h1>Opiniões da comunidade</h1>
              <p>Interaja com as opiniões da comunidade selecionando um dos botões
                de opção.</p>
            </div>
          </div>
          {this.comment ?
            <div class="Comment">
              <div class="Comment-user">
                {/* <i class="fa fa-user"></i><span>comment.author.name</span> */}
                <ion-icon name="person"></ion-icon><span>{this.comment.author_name} </span>
              </div>
              <p>{this.comment.content}</p>
              <div class='Comment-voteArea'>
                <ul class="ConversationComment-actions">
                  <li up-expand>
                    <button onClick={() => this.agree(this.comment)} >
                      {/* <i class="fa fa-check"></i> */}
                      <ion-icon name="checkmark"></ion-icon>
                    </button>
                    <span>Agree</span>
                  </li>
                  <li up-expand>
                    <button onClick={() => this.skip(this.comment)}>
                      {/* <i class="fa fa-arrow-right"></i> */}
                      <ion-icon ios="ios-arrow-forward" md="md-arrow-forward"></ion-icon>

                    </button>
                    <span>Skip</span>
                  </li>
                  <li up-expand>
                    <button onClick={() => this.disagree(this.comment)}>
                      {/* <i class="fa fa-times"></i> */}
                      <ion-icon ios="ios-close" md="md-close"></ion-icon>
                    </button>
                    <span>Disagree</span>
                  </li>
                </ul>
              </div>
            </div> : ''
          }
        </div>
      );
    }
  }
}
