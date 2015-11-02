#!/bin/bash
function query() {
  jp-linux-386 -u "$2" <<<"$1"
}
