import http from 'k6/http';

export let options = {
  vus: 1000, 
  duration: '1m',
};

export default function () {
  const url = 'http://127.0.0.1:8090/dummyLogin';
  const payload = JSON.stringify({
      "role" : "client"
  });

  const params = {
      headers: {
          'Content-Type': 'application/json',
      },
  };

  http.post(url, payload, params);
}