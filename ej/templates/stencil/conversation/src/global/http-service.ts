import { CommentModel, VoteModel } from './interfaces';


const fetchConversation = () => {
  const url = `http://localhost:8000/api/v1/conversations/random/`;

  return fetch(url).then((res) => {
    //FIXME remove this code
    // console.log('fetchConversation 1: ', res)
    return res.json()
  })
}

const getToken = () => {
  const url = `http://localhost:8000/api/v1/users/me/`;

  return fetch(url).then((res) => {
    return res.json()
  })
}

const login = (username: string, password: string ) => {
  const url = `http://localhost:8000/rest-auth/login/`;

  const user = {'username': username, 'email': 'leandronunes@gmail.com', 'password': password}

  return fetch(url, {
    method: 'post',
    body: JSON.stringify(user),
    headers: {'Content-Type': 'application/json' }

  }).then((res) => {
    return res.json()
  })
}


const fetchRandomComent = (slug: string) => {
  const url = `http://localhost:8000/api/v1/conversations/${slug}/random_comment/`;

  return fetch(url).then((res) => {
    return res.json()
  })
}

const saveVote = (comment: CommentModel, action: number) => {
  const vote = new VoteModel();
  vote.comment = comment.id.toString();
  vote.value = action;

  let token = localStorage.getItem("token").substr(1).slice(0, -1);;
  const response = fetch(`http://localhost:8000/api/v1/votes/`, {
    method: 'post',
    body: JSON.stringify(vote),
    headers: {'Content-Type': 'application/json', 'Authorization': 'Token ' + token }
  })

  return response.then((response) => {
    return response.json();
  })
}

export { fetchConversation, fetchRandomComent, getToken, saveVote, login };