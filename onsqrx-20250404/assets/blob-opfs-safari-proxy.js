self.addEventListener('message', async (ev) => {
  if (!ev.data) {
    return;
  }

  if (ev.data.call === 'read') {
    const r = await fetch(ev.data.bin);
    const blob = await r.blob();
    self.postMessage(
      {
        response: 'read',
        id: ev.data.id,
        bin: blob,
      },
      {
        transfer: [blob],
      },
    );
  } else if (ev.data.call === 'write') {
    const r = await fetch(ev.data.bin);
    const blob = await r.blob();

    var reader = new FileReader();
    reader.readAsDataURL(blob);
    reader.onloadend = function () {
      const base64data = reader.result.substring(
        reader.result.indexOf(',') + 1,
      );
      self.postMessage({
        response: 'write',
        id: ev.data.id,
        data: base64data,
      });
    };
  }
});
